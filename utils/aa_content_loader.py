"""
Alcoholics Anonymous Content Loader

This module provides utilities for loading AA content into the database,
including the Big Book text, audio versions, and speaker recordings.
The content is loaded from public domain sources and stored locally
to reduce API costs and provide reliable access.
"""

import os
import logging
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import traceback

from models.aa_content_models import (
    AABigBook,
    AABigBookAudio,
    AASpeakerRecording,
    AADailyReflection,
    db
)

# Set up logging
logger = logging.getLogger(__name__)

# Source URLs for content
BIG_BOOK_TEXT_SOURCE = "https://www.aa.org/the-big-book"
BIG_BOOK_AUDIO_SOURCE = "https://www.aa.org/audio-big-book"
AA_SPEAKERS_SOURCE = "https://silkworth.net/alcoholics-anonymous/speakers/"

class AAContentLoader:
    """Class for loading AA content into the database"""

    def __init__(self):
        """Initialize the content loader"""
        self.content_dir = os.path.join(os.getcwd(), 'static', 'aa_content')

        # Ensure content directory exists
        if not os.path.exists(self.content_dir):
            try:
                os.makedirs(self.content_dir)
                logger.info(f"Created AA content directory: {self.content_dir}")
            except Exception as e:
                logger.error(f"Failed to create AA content directory: {str(e)}")

    def load_big_book_text(self, force_reload: bool = False) -> bool:
        """
        Load the AA Big Book text content into the database

        Args:
            force_reload: Whether to force reload even if content exists

        Returns:
            bool: Success status
        """
        try:
            # Check if content already exists
            if not force_reload and db.session.query(AABigBook).count() > 0:
                logger.info("AA Big Book text already loaded, skipping")
                return True

            logger.info("Loading AA Big Book text content")

            # The Big Book 4th edition content is in the public domain
            # Here we're loading a predefined structure with chapter info
            chapters = self._get_big_book_structure()

            # Load each chapter's content
            for chapter in chapters:
                # Check if chapter already exists
                existing = AABigBook.query.filter_by(
                    chapter_number=chapter['number'],
                    edition='4th'
                ).first()

                if existing and not force_reload:
                    continue

                # Create or update chapter
                if existing:
                    existing.chapter_title = chapter['title']
                    existing.content = chapter['content']
                    existing.is_foreword = chapter.get('is_foreword', False)
                    existing.is_appendix = chapter.get('is_appendix', False)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_chapter = AABigBook(
                        chapter_number=chapter['number'],
                        chapter_title=chapter['title'],
                        content=chapter['content'],
                        is_foreword=chapter.get('is_foreword', False),
                        is_appendix=chapter.get('is_appendix', False),
                        edition='4th'
                    )
                    db.session.add(new_chapter)

            db.session.commit()
            logger.info(f"Successfully loaded {len(chapters)} Big Book chapters")
            return True

        except Exception as e:
            logger.error(f"Error loading Big Book text: {str(e)}")
            logger.error(traceback.format_exc())
            db.session.rollback()
            return False

    def load_big_book_audio(self, force_reload: bool = False) -> bool:
        """
        Load the AA Big Book audio files into the database

        Args:
            force_reload: Whether to force reload even if content exists

        Returns:
            bool: Success status
        """
        try:
            # Check if content already exists
            if not force_reload and db.session.query(AABigBookAudio).count() > 0:
                logger.info("AA Big Book audio already loaded, skipping")
                return True

            logger.info("Loading AA Big Book audio files")

            # Get audio file information
            audio_files = self._get_big_book_audio_files()

            # Download audio files if needed and add to database
            for audio_file in audio_files:
                # Get corresponding chapter
                chapter = AABigBook.query.filter_by(
                    chapter_number=audio_file['chapter_number'],
                    edition='4th'
                ).first()

                if not chapter:
                    logger.warning(f"No matching chapter found for audio: Chapter {audio_file['chapter_number']}")
                    continue

                # Check if audio file already exists
                existing = AABigBookAudio.query.filter_by(
                    chapter_id=chapter.id,
                    file_path=audio_file['file_path']
                ).first()

                if existing and not force_reload:
                    continue

                # Download the file if it doesn't exist locally
                local_path = os.path.join(self.content_dir, os.path.basename(audio_file['file_path']))
                if not os.path.exists(local_path) and 'url' in audio_file:
                    success = self._download_file(audio_file['url'], local_path)
                    if not success:
                        continue

                    # Update the file path to the local path
                    audio_file['file_path'] = f"/static/aa_content/{os.path.basename(local_path)}"

                # Create or update audio entry
                if existing:
                    existing.file_path = audio_file['file_path']
                    existing.duration_seconds = audio_file.get('duration_seconds')
                    existing.narrator = audio_file.get('narrator')
                    existing.audio_quality = audio_file.get('audio_quality')
                    existing.format = audio_file.get('format', 'mp3')
                else:
                    new_audio = AABigBookAudio(
                        chapter_id=chapter.id,
                        file_path=audio_file['file_path'],
                        duration_seconds=audio_file.get('duration_seconds'),
                        narrator=audio_file.get('narrator'),
                        audio_quality=audio_file.get('audio_quality'),
                        format=audio_file.get('format', 'mp3')
                    )
                    db.session.add(new_audio)

            db.session.commit()
            logger.info(f"Successfully loaded {len(audio_files)} Big Book audio files")
            return True

        except Exception as e:
            logger.error(f"Error loading Big Book audio: {str(e)}")
            logger.error(traceback.format_exc())
            db.session.rollback()
            return False

    def load_speaker_recordings(self, force_reload: bool = False) -> bool:
        """
        Load AA speaker recordings into the database

        Args:
            force_reload: Whether to force reload even if content exists

        Returns:
            bool: Success status
        """
        try:
            # Check if content already exists
            if not force_reload and db.session.query(AASpeakerRecording).count() > 0:
                logger.info("AA speaker recordings already loaded, skipping")
                return True

            logger.info("Loading AA speaker recordings")

            # Get speaker recording information
            recordings = self._get_speaker_recordings()

            # Download recordings if needed and add to database
            for recording in recordings:
                # Check if recording already exists
                existing = AASpeakerRecording.query.filter_by(
                    title=recording['title'],
                    speaker_name=recording['speaker_name']
                ).first()

                if existing and not force_reload:
                    continue

                # Download the file if it doesn't exist locally
                local_path = os.path.join(self.content_dir, os.path.basename(recording['file_path']))
                if not os.path.exists(local_path) and 'url' in recording:
                    success = self._download_file(recording['url'], local_path)
                    if not success:
                        continue

                    # Update the file path to the local path
                    recording['file_path'] = f"/static/aa_content/{os.path.basename(local_path)}"

                # Create or update recording entry
                if existing:
                    existing.file_path = recording['file_path']
                    existing.description = recording.get('description')
                    existing.year_recorded = recording.get('year_recorded')
                    existing.location = recording.get('location')
                    existing.duration_seconds = recording.get('duration_seconds')
                    existing.tags = recording.get('tags')
                    existing.format = recording.get('format', 'mp3')
                else:
                    new_recording = AASpeakerRecording(
                        title=recording['title'],
                        speaker_name=recording['speaker_name'],
                        file_path=recording['file_path'],
                        description=recording.get('description'),
                        year_recorded=recording.get('year_recorded'),
                        location=recording.get('location'),
                        duration_seconds=recording.get('duration_seconds'),
                        tags=recording.get('tags'),
                        format=recording.get('format', 'mp3')
                    )
                    db.session.add(new_recording)

            db.session.commit()
            logger.info(f"Successfully loaded {len(recordings)} speaker recordings")
            return True

        except Exception as e:
            logger.error(f"Error loading speaker recordings: {str(e)}")
            logger.error(traceback.format_exc())
            db.session.rollback()
            return False

    def _download_file(self, url: str, destination: str) -> bool:
        """
        Download a file from a URL to a local destination

        Args:
            url: URL to download from
            destination: Local destination path

        Returns:
            bool: Success status
        """
        try:
            # Ensure the parent directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            # Download the file in chunks
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Successfully downloaded file to {destination}")
            return True

        except Exception as e:
            logger.error(f"Error downloading file from {url}: {str(e)}")
            return False

    def _get_big_book_structure(self) -> List[Dict[str, Any]]:
        """
        Get the structure of the Big Book with content

        Returns:
            List of chapter dictionaries with content
        """
        # This would normally fetch from a reliable source or API
        # For now, we'll include a basic structure with sample content
        # In a production environment, you would load complete content

        aa_big_book_structure = [
            {
                "number": 0,
                "title": "Preface",
                "is_foreword": True,
                "content": "THIS IS the fourth edition of the book 'Alcoholics Anonymous.' The first edition appeared in April 1939, and in the following sixteen years, more than 300,000 copies went into circulation. The second edition, published in 1955, reached a total of more than 1,150,500 copies. The third edition, which came off press in 1976, achieved a circulation of approximately 19,550,000 in all formats. Because this book has become the basic text for our Society and has helped such large numbers of alcoholic men and women to recovery, there exists strong sentiment against any radical changes being made in it..."
            },
            {
                "number": 1,
                "title": "The Doctor's Opinion",
                "content": "WE OF Alcoholics Anonymous believe that the reader will be interested in the medical estimate of the plan of recovery described in this book. Convincing testimony must surely come from medical men who have had experience with the sufferings of our members and have witnessed our return to health..."
            },
            {
                "number": 2,
                "title": "Bill's Story",
                "content": "WAR FEVER ran high in the New England town to which we new, young officers from Plattsburg were assigned, and we were flattered when the first citizens took us to their homes, making us feel heroic. Here was love, applause, war; moments sublime with intervals hilarious. I was part of life at last, and in the midst of the excitement I discovered liquor..."
            },
            {
                "number": 3,
                "title": "There Is A Solution",
                "content": "WE, OF ALCOHOLICS ANONYMOUS, know thousands of men and women who were once just as hopeless as Bill. Nearly all have recovered. They have solved the drink problem. We are average Americans. All sections of this country and many of its occupations are represented, as well as many political, economic, social, and religious backgrounds..."
            },
            {
                "number": 4,
                "title": "We Agnostics",
                "content": "IN THE PRECEDING chapters you have learned something of alcoholism. We hope we have made clear the distinction between the alcoholic and the non-alcoholic. If, when you honestly want to, you find you cannot quit entirely, or if when drinking, you have little control over the amount you take, you are probably alcoholic..."
            },
            {
                "number": 5,
                "title": "How It Works",
                "content": "RARELY HAVE we seen a person fail who has thoroughly followed our path. Those who do not recover are people who cannot or will not completely give themselves to this simple program, usually men and women who are constitutionally incapable of being honest with themselves..."
            },
            {
                "number": 17,
                "title": "Doctor Bob's Nightmare",
                "content": "I WAS born in a small New England village of about seven thousand souls. The general moral standard was, as I recall it, far above the average. No beer or liquor was sold in the neighborhood, except at the State liquor agency where perhaps one might procure a pint if he could convince the agent that he really needed it..."
            },
            {
                "number": 30,
                "title": "Appendix I: The A.A. Tradition",
                "is_appendix": True,
                "content": "To those now in its fold, Alcoholics Anonymous has made the difference between misery and sobriety, and often the difference between life and death. A.A. can, of course, mean just as much to uncounted alcoholics not yet reached. Therefore, no society of men and women ever had a more urgent need for continuous effectiveness and permanent unity..."
            },
            {
                "number": 31,
                "title": "Appendix II: Spiritual Experience",
                "is_appendix": True,
                "content": "The terms \"spiritual experience\" and \"spiritual awakening\" are used many times in this book which, upon careful reading, shows that the personality change sufficient to bring about recovery from alcoholism has manifested itself among us in many different forms..."
            }
        ]

        return aa_big_book_structure

    def _get_big_book_audio_files(self) -> List[Dict[str, Any]]:
        """
        Get information about Big Book audio files

        Returns:
            List of audio file dictionaries
        """
        # This would normally fetch from a reliable source or API
        # For now, we'll include basic sample data
        # In a production environment, you would include actual file data

        audio_files = [
            {
                "chapter_number": 0,
                "file_path": "/static/aa_content/preface.mp3",
                "duration_seconds": 540,  # 9 minutes
                "narrator": "AA World Services",
                "audio_quality": "High",
                "format": "mp3"
            },
            {
                "chapter_number": 1,
                "file_path": "/static/aa_content/doctors_opinion.mp3",
                "duration_seconds": 1320,  # 22 minutes
                "narrator": "AA World Services",
                "audio_quality": "High",
                "format": "mp3"
            },
            {
                "chapter_number": 5,
                "file_path": "/static/aa_content/how_it_works.mp3",
                "duration_seconds": 1560,  # 26 minutes
                "narrator": "AA World Services",
                "audio_quality": "High",
                "format": "mp3"
            }
        ]

        return audio_files

    def _get_speaker_recordings(self) -> List[Dict[str, Any]]:
        """
        Get information about AA speaker recordings

        Returns:
            List of recording dictionaries
        """
        # This would normally fetch from a reliable source or API
        # For now, we'll include basic sample data
        # In a production environment, you would include actual file data

        recordings = [
            {
                "title": "Recovery Story - Gratitude in Sobriety",
                "speaker_name": "Bill W.",
                "file_path": "/static/aa_content/bill_w_gratitude.mp3",
                "description": "Bill W. shares his story of recovery and the importance of gratitude in maintaining sobriety.",
                "year_recorded": 1960,
                "location": "AA International Convention",
                "duration_seconds": 2400,  # 40 minutes
                "tags": "founders,gratitude,12steps",
                "format": "mp3"
            },
            {
                "title": "Our Primary Purpose",
                "speaker_name": "Dr. Bob",
                "file_path": "/static/aa_content/dr_bob_purpose.mp3",
                "description": "Dr. Bob discusses the primary purpose of AA and helping other alcoholics to achieve sobriety.",
                "year_recorded": 1950,
                "location": "Cleveland, OH",
                "duration_seconds": 1800,  # 30 minutes
                "tags": "founders,service,helping_others",
                "format": "mp3"
            },
            {
                "title": "Emotional Sobriety",
                "speaker_name": "John D.",
                "file_path": "/static/aa_content/john_d_emotional.mp3",
                "description": "A powerful talk on achieving emotional sobriety beyond just not drinking.",
                "year_recorded": 1975,
                "location": "Los Angeles, CA",
                "duration_seconds": 3000,  # 50 minutes
                "tags": "emotional_sobriety,long_term_recovery,serenity",
                "format": "mp3"
            }
        ]

        return recordings

    def load_all_content(self, force_reload: bool = False) -> Dict[str, bool]:
        """
        Load all AA content into the database

        Args:
            force_reload: Whether to force reload even if content exists

        Returns:
            Dict with status of each content type
        """
        results = {
            "big_book_text": self.load_big_book_text(force_reload),
            "big_book_audio": self.load_big_book_audio(force_reload),
            "speaker_recordings": self.load_speaker_recordings(force_reload)
        }

        return results

# Create an instance for easy import
aa_content_loader = AAContentLoader()

def get_aa_content_loader() -> AAContentLoader:
    """Get the global AA content loader instance"""
    global aa_content_loader
    return aa_content_loader

def load_aa_content(force_reload: bool = False) -> Dict[str, bool]:
    """
    Convenience function to load all AA content

    Args:
        force_reload: Whether to force reload even if content exists

    Returns:
        Dict with status of each content type
    """
    return aa_content_loader.load_all_content(force_reload)