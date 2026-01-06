#!/usr/bin/env python3
"""
Demo Data Seed Script for NOUS Intelligence
Creates sample CBT thought records and mood logs for demo purposes
"""

from datetime import datetime, timedelta
import random

def seed_demo_data():
    """Seed demo data for testing/demo purposes"""
    
    from app import app, db
    from models.health_models import CBTThoughtRecord, CBTMoodLog
    
    with app.app_context():
        print("🌱 Seeding demo data for NOUS Intelligence...")
        
        # Demo user ID
        demo_user_id = "demo_user"
        
        # Sample thought records
        thought_records_data = [
            {
                'situation': "Got critical feedback on my project at work",
                'automatic_thought': "I'm terrible at my job. I'm going to get fired.",
                'emotion': 'anxious',
                'emotion_intensity': 8,
                'evidence_for': "The feedback pointed out several mistakes I made",
                'evidence_against': "My manager also mentioned things I did well. This is my first time working on this type of project. Everyone makes mistakes when learning.",
                'balanced_thought': "I made some mistakes on a new type of project, which is normal when learning. The feedback will help me improve. My manager also recognized what I did well.",
                'new_emotion': 'concerned',
                'new_emotion_intensity': 4,
            },
            {
                'situation': "Friend didn't respond to my text for 2 days",
                'automatic_thought': "They must be mad at me. I did something wrong.",
                'emotion': 'worried',
                'emotion_intensity': 7,
                'evidence_for': "They usually respond quickly. It's been 2 days.",
                'evidence_against': "They mentioned being busy with exams. They haven't seemed upset in recent conversations. I haven't done anything that would upset them.",
                'balanced_thought': "They're probably just busy with exams like they mentioned. If something was wrong, they would talk to me about it.",
                'new_emotion': 'calm',
                'new_emotion_intensity': 3,
            },
            {
                'situation': "Made a small mistake in presentation",
                'automatic_thought': "Everyone thinks I'm incompetent. The whole presentation was ruined.",
                'emotion': 'ashamed',
                'emotion_intensity': 9,
                'evidence_for': "I stumbled over my words and lost my place",
                'evidence_against': "The mistake was brief. I recovered quickly. People seemed engaged with the content. I received positive feedback afterward.",
                'balanced_thought': "I made a small mistake but recovered well. The overall presentation was successful based on the positive feedback.",
                'new_emotion': 'neutral',
                'new_emotion_intensity': 2,
            },
        ]
        
        # Sample mood logs
        mood_logs_data = [
            {'mood': 'anxious', 'intensity': 7, 'triggers': 'Work deadline approaching', 'notes': 'Feeling overwhelmed'},
            {'mood': 'calm', 'intensity': 3, 'triggers': 'Morning meditation', 'notes': 'Started day with breathing exercises'},
            {'mood': 'frustrated', 'intensity': 6, 'triggers': 'Traffic jam', 'notes': 'Late to meeting'},
            {'mood': 'happy', 'intensity': 8, 'triggers': 'Finished project successfully', 'notes': 'Team celebrated together'},
            {'mood': 'sad', 'intensity': 5, 'triggers': 'Missing family', 'notes': 'Haven\'t seen them in months'},
            {'mood': 'stressed', 'intensity': 8, 'triggers': 'Multiple deadlines', 'notes': 'Need to prioritize tasks'},
            {'mood': 'content', 'intensity': 4, 'triggers': 'Quiet evening at home', 'notes': 'Reading and relaxing'},
            {'mood': 'worried', 'intensity': 6, 'triggers': 'Health concern', 'notes': 'Scheduled doctor appointment'},
            {'mood': 'excited', 'intensity': 7, 'triggers': 'Planning vacation', 'notes': 'Looking forward to time off'},
            {'mood': 'grateful', 'intensity': 8, 'triggers': 'Friend helped me', 'notes': 'Appreciating my support system'},
        ]
        
        # Create thought records
        print("📝 Creating sample thought records...")
        for i, data in enumerate(thought_records_data):
            record = CBTThoughtRecord(
                user_id=demo_user_id,
                date=(datetime.utcnow() - timedelta(days=len(thought_records_data) - i)).date(),
                **data
            )
            db.session.add(record)
            print(f"  ✅ Created thought record: {data['situation'][:50]}...")
        
        # Create mood logs with varied timestamps
        print("\n💭 Creating sample mood logs...")
        for i, data in enumerate(mood_logs_data):
            mood_log = CBTMoodLog(
                user_id=demo_user_id,
                timestamp=datetime.utcnow() - timedelta(days=len(mood_logs_data) - i, hours=random.randint(0, 23)),
                **data
            )
            db.session.add(mood_log)
            print(f"  ✅ Created mood log: {data['mood']} ({data['intensity']}/10)")
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n✨ Demo data seeded successfully!")
            print(f"\n📊 Summary:")
            print(f"  - {len(thought_records_data)} thought records created")
            print(f"  - {len(mood_logs_data)} mood logs created")
            print(f"  - User ID: {demo_user_id}")
            print(f"\n💡 You can now demo CBT features with pre-populated data!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error seeding data: {e}")
            raise

if __name__ == '__main__':
    seed_demo_data()
