import base64
import io
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from collections import Counter

# Set seaborn style for better aesthetics
from utils.auth_compat import get_demo_user
sns.set_style("darkgrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'axes.facecolor': '#f0f0f0',
    'figure.facecolor': '#f8f8f8',
})

def generate_top_artists_chart(spotify, time_range='medium_term', limit=10):
    """
    Generate a horizontal bar chart of the user's top artists

    Args:
        spotify: Authenticated Spotify client
        time_range: 'short_term', 'medium_term', or 'long_term'
        limit: Number of artists to include

    Returns:
        base64 encoded PNG image
    """
    try:
        top_artists = spotify.get_demo_user()_top_artists(limit=limit, time_range=time_range)

        if not top_artists['items']:
            return None

        # Extract artist names and popularity
        names = [artist['name'] for artist in top_artists['items']]
        popularity = [artist['popularity'] for artist in top_artists['items']]

        # Create DataFrame
        df = pd.DataFrame({
            'Artist': names,
            'Popularity': popularity
        })

        # Sort by popularity
        df = df.sort_values('Popularity', ascending=True)

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot horizontal bar chart
        bars = sns.barplot(x='Popularity', y='Artist', data=df, palette='viridis', ax=ax)

        # Add value labels to the bars
        for i, p in enumerate(bars.patches):
            width = p.get_width()
            ax.text(width + 1, p.get_y() + p.get_height()/2, f'{int(width)}',
                    ha='left', va='center')

        # Set title and labels
        time_labels = {
            'short_term': 'Recent (4 weeks)',
            'medium_term': 'Last 6 Months',
            'long_term': 'All Time'
        }
        ax.set_title(f'Your Top {limit} Artists - {time_labels.get(time_range, time_range)}',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Popularity Score', fontsize=12)
        ax.set_ylabel('', fontsize=12)

        # Remove top and right spines
        sns.despine(left=True)

        # Add a subtle grid
        ax.grid(axis='x', linestyle='--', alpha=0.7)

        # Tight layout
        plt.tight_layout()

        # Convert plot to PNG image
        img = io_to_base64(fig)
        plt.close(fig)

        return img
    except Exception as e:
        logging.error(f"Error generating top artists chart: {str(e)}")
        return None

def generate_top_tracks_chart(spotify, time_range='medium_term', limit=10):
    """
    Generate a horizontal bar chart of the user's top tracks

    Args:
        spotify: Authenticated Spotify client
        time_range: 'short_term', 'medium_term', or 'long_term'
        limit: Number of tracks to include

    Returns:
        base64 encoded PNG image
    """
    try:
        top_tracks = spotify.get_demo_user()_top_tracks(limit=limit, time_range=time_range)

        if not top_tracks['items']:
            return None

        # Extract track names and artists
        track_names = [f"{track['name']}" for track in top_tracks['items']]
        artists = [track['artists'][0]['name'] for track in top_tracks['items']]
        popularity = [track['popularity'] for track in top_tracks['items']]

        # Combine track and artist for y-axis labels
        labels = [f"{track} - {artist}" for track, artist in zip(track_names, artists)]

        # Create DataFrame
        df = pd.DataFrame({
            'Track': labels,
            'Popularity': popularity
        })

        # Sort by popularity
        df = df.sort_values('Popularity', ascending=True)

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot horizontal bar chart
        bars = sns.barplot(x='Popularity', y='Track', data=df, palette='magma', ax=ax)

        # Add value labels to the bars
        for i, p in enumerate(bars.patches):
            width = p.get_width()
            ax.text(width + 1, p.get_y() + p.get_height()/2, f'{int(width)}',
                    ha='left', va='center')

        # Set title and labels
        time_labels = {
            'short_term': 'Recent (4 weeks)',
            'medium_term': 'Last 6 Months',
            'long_term': 'All Time'
        }
        ax.set_title(f'Your Top {limit} Tracks - {time_labels.get(time_range, time_range)}',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Popularity Score', fontsize=12)
        ax.set_ylabel('', fontsize=12)

        # Remove top and right spines
        sns.despine(left=True)

        # Add a subtle grid
        ax.grid(axis='x', linestyle='--', alpha=0.7)

        # Tight layout
        plt.tight_layout()

        # Convert plot to PNG image
        img = io_to_base64(fig)
        plt.close(fig)

        return img
    except Exception as e:
        logging.error(f"Error generating top tracks chart: {str(e)}")
        return None

def generate_genre_chart(spotify, limit=10):
    """
    Generate a pie chart of the user's top genres based on their top artists

    Args:
        spotify: Authenticated Spotify client
        limit: Number of genres to include

    Returns:
        base64 encoded PNG image
    """
    try:
        # Get user's top artists from different time periods for more data
        top_artists_short = spotify.get_demo_user()_top_artists(limit=50, time_range='short_term')
        top_artists_medium = spotify.get_demo_user()_top_artists(limit=50, time_range='medium_term')
        top_artists_long = spotify.get_demo_user()_top_artists(limit=50, time_range='long_term')

        # Combine all artists
        all_artists = []
        artist_ids = set()  # To avoid duplicates

        for artists_data in [top_artists_short, top_artists_medium, top_artists_long]:
            for artist in artists_data['items']:
                if artist['id'] not in artist_ids:
                    all_artists.append(artist)
                    artist_ids.add(artist['id'])

        if not all_artists:
            return None

        # Extract all genres
        all_genres = []
        for artist in all_artists:
            all_genres.extend(artist['genres'])

        # Count genre frequencies
        genre_counter = Counter(all_genres)
        top_genres = genre_counter.most_common(limit)

        # Create DataFrame
        df = pd.DataFrame(top_genres, columns=['Genre', 'Count'])

        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 10))

        # Use custom colors for the pie chart
        colors = plt.cm.viridis(np.linspace(0, 1, len(df)))

        # Plot
        wedges, texts, autotexts = ax.pie(
            df['Count'],
            labels=df['Genre'],
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1},
            textprops={'fontsize': 12},
            colors=colors
        )

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        plt.setp(autotexts, size=10, weight='bold')

        # Add title
        ax.set_title('Your Top Music Genres', fontsize=16, fontweight='bold', pad=20)

        # Tight layout
        plt.tight_layout()

        # Convert plot to PNG image
        img = io_to_base64(fig)
        plt.close(fig)

        return img
    except Exception as e:
        logging.error(f"Error generating genre chart: {str(e)}")
        return None

def generate_listening_history_chart(spotify, limit=50):
    """
    Generate a line chart showing listening patterns based on recently played tracks

    Args:
        spotify: Authenticated Spotify client
        limit: Maximum number of recently played tracks to analyze

    Returns:
        base64 encoded PNG image
    """
    try:
        # Get recently played tracks
        recent = spotify.get_demo_user()_recently_played(limit=limit)

        if not recent['items']:
            return None

        # Extract timestamps and convert to datetime
        timestamps = [pd.to_datetime(item['played_at']) for item in recent['items']]

        # Count plays per day
        dates = [ts.date() for ts in timestamps]
        date_counts = Counter(dates)

        # Create DataFrame
        df = pd.DataFrame({
            'Date': list(date_counts.keys()),
            'Plays': list(date_counts.values())
        }).sort_values('Date')

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot line chart
        sns.lineplot(x='Date', y='Plays', data=df, marker='o', color='#1DB954', ax=ax)

        # Set title and labels
        ax.set_title('Your Listening Activity', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Tracks Played', fontsize=12)

        # Format x-axis
        plt.xticks(rotation=45)

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)

        # Tight layout
        plt.tight_layout()

        # Convert plot to PNG image
        img = io_to_base64(fig)
        plt.close(fig)

        return img
    except Exception as e:
        logging.error(f"Error generating listening history chart: {str(e)}")
        return None

def generate_audio_features_radar_chart(spotify, track_id=None):
    """
    Generate a radar chart of audio features for a specific track
    If no track_id is provided, uses the currently playing track

    Args:
        spotify: Authenticated Spotify client
        track_id: Optional Spotify track ID

    Returns:
        base64 encoded PNG image and track info
    """
    try:
        # Get track info
        if not track_id:
            current = spotify.current_playback()
            if not current or not current.get('item'):
                # Use the most recently played track as fallback
                recent = spotify.get_demo_user()_recently_played(limit=1)
                if not recent['items']:
                    return None, None
                track_id = recent['items'][0]['track']['id']
                track_name = recent['items'][0]['track']['name']
                artist_name = recent['items'][0]['track']['artists'][0]['name']
            else:
                track_id = current['item']['id']
                track_name = current['item']['name']
                artist_name = current['item']['artists'][0]['name']
        else:
            track = spotify.track(track_id)
            track_name = track['name']
            artist_name = track['artists'][0]['name']

        # Get audio features
        features = spotify.audio_features(track_id)[0]

        if not features:
            return None, None

        # Select relevant features for radar chart
        selected_features = {
            'Danceability': features['danceability'],
            'Energy': features['energy'],
            'Acousticness': features['acousticness'],
            'Instrumentalness': features['instrumentalness'],
            'Liveness': features['liveness'],
            'Valence': features['valence']
        }

        # Convert to DataFrame
        df = pd.DataFrame({
            'Feature': list(selected_features.keys()),
            'Value': list(selected_features.values())
        })

        # Number of variables
        N = len(df)

        # Create figure
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, polar=True)

        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop

        # Add values
        values = df['Value'].tolist()
        values += values[:1]  # Close the loop

        # Draw the plot
        ax.plot(angles, values, linewidth=2, linestyle='solid', color='#1DB954')
        ax.fill(angles, values, alpha=0.25, color='#1DB954')

        # Add labels
        plt.xticks(angles[:-1], df['Feature'], size=12)

        # Draw y-labels (0-1)
        ax.set_rlabel_position(0)
        plt.yticks([0.2, 0.4, 0.6, 0.8], ['0.2', '0.4', '0.6', '0.8'], color='grey', size=10)
        plt.ylim(0, 1)

        # Add title
        plt.title(f'Audio Features: {track_name} - {artist_name}',
                 size=16, fontweight='bold', pad=30)

        # Show additional features as text
        additional_features = {
            'Key': features['key'],
            'Mode': 'Major' if features['mode'] == 1 else 'Minor',
            'Tempo': f"{int(features['tempo'])} BPM",
            'Loudness': f"{features['loudness']} dB",
            'Time Signature': f"{features['time_signature']}/4"
        }

        feature_text = "\n".join([f"{k}: {v}" for k, v in additional_features.items()])
        plt.figtext(0.95, 0.05, feature_text, ha='right', fontsize=10)

        # Tight layout
        plt.tight_layout()

        # Convert plot to PNG image
        img = io_to_base64(fig)
        plt.close(fig)

        return img, {'name': track_name, 'artist': artist_name}
    except Exception as e:
        logging.error(f"Error generating audio features chart: {str(e)}")
        return None, None

def generate_playlist_mood_analysis(spotify, playlist_id):
    """
    Generate charts analyzing the mood and characteristics of a playlist

    Args:
        spotify: Authenticated Spotify client
        playlist_id: Spotify playlist ID

    Returns:
        Dictionary with base64 encoded PNG images
    """
    try:
        # Get playlist details
        playlist = spotify.playlist(playlist_id)

        if not playlist or not playlist.get('tracks') or not playlist['tracks'].get('items'):
            return None

        # Extract track IDs
        track_ids = []
        for item in playlist['tracks']['items']:
            if item.get('track') and item['track'].get('id'):
                track_ids.append(item['track']['id'])

        if not track_ids:
            return None

        # Get audio features for all tracks (in batches of 100)
        all_features = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            features = spotify.audio_features(batch)
            all_features.extend([f for f in features if f])

        if not all_features:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(all_features)

        results = {}

        # 1. Energy vs Valence scatter plot (Energy-Mood matrix)
        fig, ax = plt.subplots(figsize=(10, 8))

        scatter = ax.scatter(
            df['valence'],
            df['energy'],
            c=df['danceability'],
            cmap='viridis',
            alpha=0.7,
            s=100
        )

        # Add a colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Danceability', rotation=270, labelpad=20)

        # Add quadrant lines and labels
        ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)

        # Add quadrant annotations
        ax.text(0.25, 0.75, 'Angry/Energetic', fontsize=12, ha='center')
        ax.text(0.75, 0.75, 'Happy/Joyful', fontsize=12, ha='center')
        ax.text(0.25, 0.25, 'Sad/Depressing', fontsize=12, ha='center')
        ax.text(0.75, 0.25, 'Calm/Relaxing', fontsize=12, ha='center')

        # Set title and labels
        ax.set_title(f'Mood Analysis: {playlist["name"]}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Valence (Positivity)', fontsize=12)
        ax.set_ylabel('Energy', fontsize=12)

        # Set axis limits
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        plt.tight_layout()

        # Convert plot to PNG image
        results['mood_matrix'] = io_to_base64(fig)
        plt.close(fig)

        # 2. Distribution of key audio features
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))

        features_to_plot = ['energy', 'danceability', 'valence', 'tempo']
        titles = ['Energy Distribution', 'Danceability Distribution',
                 'Valence (Positivity) Distribution', 'Tempo Distribution (BPM)']
        colors = ['#1DB954', '#4F86C6', '#8A4F9E', '#D85040']

        for i, (feature, title, color) in enumerate(zip(features_to_plot, titles, colors)):
            row, col = i // 2, i % 2

            # For tempo, normalize to 0-1 for KDE
            if feature == 'tempo':
                data = df[feature] / df[feature].max()
                # Create histogram
                sns.histplot(data, kde=True, color=color, ax=axs[row, col], stat='density')
                # Create custom x-tick labels showing actual BPM values
                ticks = np.linspace(0, 1, 5)
                tick_labels = [f"{int(t * df['tempo'].max())}" for t in ticks]
                axs[row, col].set_xticks(ticks)
                axs[row, col].set_xticklabels(tick_labels)
            else:
                sns.histplot(df[feature], kde=True, color=color, ax=axs[row, col], stat='density')

            axs[row, col].set_title(title)

            # Set x-limits for consistency (except tempo)
            if feature != 'tempo':
                axs[row, col].set_xlim(0, 1)

        plt.suptitle(f'Audio Feature Distributions: {playlist["name"]}',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()

        # Convert plot to PNG image
        results['feature_distributions'] = io_to_base64(fig)
        plt.close(fig)

        # 3. Summary statistics
        stats = {
            'track_count': len(df),
            'avg_duration_min': df['duration_ms'].mean() / 60000,
            'avg_energy': df['energy'].mean(),
            'avg_danceability': df['danceability'].mean(),
            'avg_valence': df['valence'].mean(),
            'avg_tempo': df['tempo'].mean(),
            'dominant_key': df['key'].mode()[0] if not df['key'].empty else None,
            'most_common_time_signature': df['time_signature'].mode()[0] if not df['time_signature'].empty else None
        }

        return {
            'charts': results,
            'stats': stats,
            'playlist_name': playlist['name'],
            'playlist_owner': playlist['owner']['display_name']
        }
    except Exception as e:
        logging.error(f"Error generating playlist mood analysis: {str(e)}")
        return None

def generate_spotify_listening_report(spotify):
    """
    Generate a comprehensive listening report with multiple visualizations

    Args:
        spotify: Authenticated Spotify client

    Returns:
        Dictionary with base64 encoded PNG images
    """
    try:
        results = {}

        # Get top artists chart
        results['top_artists_short'] = generate_top_artists_chart(spotify, 'short_term', 10)
        results['top_artists_long'] = generate_top_artists_chart(spotify, 'long_term', 10)

        # Get top tracks chart
        results['top_tracks_short'] = generate_top_tracks_chart(spotify, 'short_term', 10)
        results['top_tracks_long'] = generate_top_tracks_chart(spotify, 'long_term', 10)

        # Get genre chart
        results['genre_chart'] = generate_genre_chart(spotify)

        # Get listening history chart
        results['listening_history'] = generate_listening_history_chart(spotify)

        # Get audio features for current track
        img, track_info = generate_audio_features_radar_chart(spotify)
        if img:
            results['current_track_features'] = img
            results['current_track_info'] = track_info

        return results
    except Exception as e:
        logging.error(f"Error generating Spotify listening report: {str(e)}")
        return None

def generate_audio_feature_comparison(spotify, track_ids, track_names=None):
    """
    Generate a comparison of audio features between multiple tracks

    Args:
        spotify: Authenticated Spotify client
        track_ids: List of Spotify track IDs
        track_names: Optional list of track names (will fetch if not provided)

    Returns:
        base64 encoded PNG image
    """
    try:
        if not track_ids:
            return None

        # Get audio features for all tracks
        features = spotify.audio_features(track_ids)
        features = [f for f in features if f]  # Filter out None values

        if not features:
            return None

        # Get track names if not provided
        if not track_names:
            track_names = []
            tracks_info = spotify.tracks(track_ids)['tracks']
            for track in tracks_info:
                if track:
                    track_names.append(f"{track['name']} - {track['artists'][0]['name']}")
                else:
                    track_names.append("Unknown Track")

        # Select features to compare
        selected_features = ['danceability', 'energy', 'acousticness',
                           'instrumentalness', 'liveness', 'valence']

        # Create DataFrame
        data = []
        for i, feature_dict in enumerate(features):
            if feature_dict:
                feature_values = {key: feature_dict[key] for key in selected_features}
                feature_values['Track'] = track_names[i] if i < len(track_names) else f"Track {i+1}"
                data.append(feature_values)

        df = pd.DataFrame(data)

        # Melt DataFrame for easier plotting
        df_melted = pd.melt(df, id_vars=['Track'], value_vars=selected_features,
                           var_name='Feature', value_name='Value')

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot grouped bar chart
        sns.barplot(x='Feature', y='Value', hue='Track', data=df_melted, ax=ax)

        # Set title and labels
        ax.set_title('Audio Feature Comparison', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Feature', fontsize=12)
        ax.set_ylabel('Value (0-1 Scale)', fontsize=12)

        # Adjust legend
        plt.legend(title='Track', bbox_to_anchor=(1.05, 1), loc='upper left')

        # Rotate x-labels
        plt.xticks(rotation=45)

        # Tight layout
        plt.tight_layout()

        # Convert plot to PNG image
        img = io_to_base64(fig)
        plt.close(fig)

        return img
    except Exception as e:
        logging.error(f"Error generating audio feature comparison: {str(e)}")
        return None

def io_to_base64(fig):
    """Convert matplotlib figure to base64 encoded string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str