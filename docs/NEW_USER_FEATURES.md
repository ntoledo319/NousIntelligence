# New User Features Documentation

## Overview

This document describes the new user features added to the NOUS platform to enhance user engagement, community building, and personal development.

## Feature Categories

### 1. Social & Community Features 🤝

#### Support Groups
- **Purpose**: Create safe spaces for users to connect over shared experiences
- **Features**:
  - Create and join support groups by category (anxiety, depression, addiction, etc.)
  - Public, private, and invite-only group privacy levels
  - Group posts and discussions
  - Moderation tools for group admins
  - Member notifications

#### Peer Connections
- **Purpose**: Build supportive relationships between users
- **Types**:
  - Peer connections (friends)
  - Mentor/mentee relationships
- **Features**:
  - Send and accept connection requests
  - View connection profiles
  - Private messaging (future feature)

#### Anonymous Sharing
- **Purpose**: Allow users to share experiences without revealing identity
- **Features**:
  - Share stories anonymously
  - Categorize shares (anxiety, success, hope, etc.)
  - Support reactions from community
  - Moderation through hashed tracking

### 2. Gamification Features 🎮

#### Achievements & Badges
- **Purpose**: Recognize and celebrate user progress
- **Categories**:
  - Wellness achievements
  - Social achievements
  - Learning achievements
  - Consistency achievements
- **Rarity Levels**: Common, Rare, Epic, Legendary

#### Points & Levels
- **Purpose**: Quantify progress and engagement
- **Point Categories**:
  - Wellness points
  - Social points
  - Learning points
  - Consistency points
- **Level System**: Progressive levels with increasing point requirements

#### Wellness Streaks
- **Purpose**: Encourage consistent healthy behaviors
- **Tracked Activities**:
  - Mood logging
  - Meditation
  - Exercise
  - Journaling
  - DBT/CBT skills practice

#### Leaderboards
- **Purpose**: Foster friendly competition
- **Types**:
  - Weekly leaderboards
  - Monthly leaderboards
  - Category-specific leaderboards
- **Privacy**: Optional participation

#### Challenges
- **Purpose**: Time-limited goals for community engagement
- **Types**:
  - Daily challenges
  - Weekly challenges
  - Monthly challenges
- **Rewards**: Bonus points and special achievements

### 3. Personal Growth Features 🌱

#### Goal Setting & Tracking
- **Purpose**: Help users achieve personal objectives
- **Features**:
  - SMART goal framework
  - Progress tracking
  - Milestone setting
  - Goal categories (health, career, personal, etc.)
  - Sub-goals and goal hierarchies

#### Habit Tracking
- **Purpose**: Build and maintain positive habits
- **Features**:
  - Daily/weekly/custom frequency habits
  - Progress visualization
  - Streak tracking
  - Reminder notifications
  - Habit categories

#### Journaling
- **Purpose**: Encourage self-reflection and emotional processing
- **Entry Types**:
  - General journal entries
  - Gratitude journals
  - Reflection journals
  - Dream journals
- **Features**:
  - Mood tracking
  - Emotion tags
  - Reflection prompts
  - Private/encrypted entries
  - Attachments (future feature)

#### Vision Boards
- **Purpose**: Visualize goals and aspirations
- **Features**:
  - Create multiple vision boards
  - Add images, text, and quotes
  - Link items to goals
  - Public/private boards
  - Drag-and-drop interface

### 4. Mental Health Resources 🏥

#### Crisis Support (Always Accessible)
- **Purpose**: Provide immediate help in mental health emergencies
- **Features**:
  - 24/7 crisis hotlines and text lines
  - No authentication required
  - Multiple crisis resources always shown
  - Country-specific resources
  - Specialized support (veterans, LGBTQ+, etc.)

#### Therapy Provider Search
- **Purpose**: Find affordable therapy options
- **Features**:
  - Location-based search
  - Filter by sliding scale/insurance
  - Specialization filtering
  - Online/in-person options
  - Distance calculation
  - Save preferred providers

#### Psychiatry Provider Search
- **Purpose**: Find medication management providers
- **Features**:
  - Location-based search
  - Medicare/Medicaid filtering
  - Telehealth options
  - Board certification info
  - New patient availability

#### Community Resources
- **Purpose**: Access free/low-cost mental health services
- **Features**:
  - Local support groups
  - Community clinics
  - Peer support services
  - Free counseling options

## API Endpoints

### Social Endpoints
```
GET  /social/groups                      - View support groups
POST /api/social/groups                  - Create support group
POST /api/social/groups/:id/join         - Join support group
GET  /social/connections                 - View connections
POST /api/social/connections/request     - Request connection
POST /api/social/connections/:id/accept  - Accept connection
GET  /social/share                       - View anonymous shares
POST /api/social/shares                  - Create anonymous share
POST /api/social/shares/:id/support      - Add support to share
```

### Gamification Endpoints
```
GET  /gamification/                      - Gamification dashboard
GET  /api/gamification/achievements      - Get user achievements
GET  /api/gamification/points           - Get points summary
GET  /api/gamification/streaks          - Get user streaks
GET  /api/gamification/leaderboard      - Get leaderboard
POST /api/gamification/challenges/:id/join - Join challenge
```

### Personal Growth Endpoints
```
GET  /growth/                           - Growth dashboard
POST /api/growth/goals                  - Create goal
PUT  /api/growth/goals/:id/progress     - Update goal progress
POST /api/growth/habits                 - Create habit
POST /api/growth/habits/:id/log         - Log habit completion
POST /api/growth/journal                - Create journal entry
POST /api/growth/vision-boards          - Create vision board
```

### Mental Health Resources Endpoints
```
GET  /resources/crisis                  - Crisis resources (NO AUTH REQUIRED)
GET  /api/crisis                        - Crisis API (NO AUTH REQUIRED)
POST /api/therapy/search                - Search therapy providers
POST /api/psychiatry/search             - Search psychiatry providers
GET  /api/community/:city/:state        - Get community resources
POST /api/resources/save                - Save a resource
GET  /api/resources/saved               - Get saved resources
```

## Implementation Guide

### Running the Migration
```bash
python migrations/add_user_features_tables.py
```

### Integrating with Existing Features

1. **Authentication**: All features use the existing authentication system
2. **Notifications**: Integrated with existing notification service
3. **AI Assistant**: Can reference user's goals, habits, and progress
4. **Analytics**: New features feed into existing analytics system

### Security Considerations

1. **Anonymous Sharing**: User IDs are hashed with date for moderation
2. **Privacy Settings**: Users control visibility of achievements and boards
3. **Group Moderation**: Admin tools for managing group content
4. **Data Encryption**: Journal entries can be encrypted
5. **Crisis Resources**: Always accessible without authentication
6. **Location Privacy**: Location data only used for search, not stored

## UI/UX Guidelines

### Navigation
Add new menu items:
- Community (for social features)
- Progress (for gamification)
- Growth (for personal development)
- Resources (for mental health support - prominently displayed)

### Mobile Responsiveness
All features should be mobile-friendly with:
- Touch-optimized interfaces
- Simplified layouts for small screens
- Offline capability for journaling

### Accessibility
- ARIA labels for all interactive elements
- Keyboard navigation support
- High contrast mode support
- Screen reader compatibility

### Crisis Support Visibility
- Crisis resources link should be visible on all pages
- Use recognizable crisis support iconography
- Clear, non-stigmatizing language
- Quick access button in chat interface

## Future Enhancements

1. **Social Features**:
   - Private messaging between connections
   - Video support groups
   - Expert-led group sessions

2. **Gamification**:
   - Custom challenges creation
   - Team challenges
   - Reward marketplace

3. **Personal Growth**:
   - AI-powered goal recommendations
   - Progress insights and analytics
   - Integration with wearables

## Monitoring & Analytics

Track these metrics:
- User engagement rates
- Feature adoption
- Streak retention
- Achievement completion rates
- Community health metrics

## Support & Troubleshooting

Common issues:
1. **Migration fails**: Check database permissions
2. **Routes not loading**: Ensure blueprints are registered
3. **Points not updating**: Check gamification service initialization

For support, check logs in:
- Application logs for errors
- Database logs for migration issues
- Service logs for business logic errors

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Status**: Ready for deployment 