"""
Intelligent Automation Workflows
Leverages existing task management + notification system + plugin architecture
to create if-this-then-that automation using existing features
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import re
from enum import Enum

from utils.unified_ai_service import UnifiedAIService
from utils.notification_service import NotificationService
from utils.weather_helper import WeatherHelper
from services.predictive_analytics import predictive_engine
from models.database import db

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    TIME = "time"
    WEATHER = "weather"
    LOCATION = "location"
    EMOTION = "emotion"
    TASK_COMPLETION = "task_completion"
    CALENDAR_EVENT = "calendar_event"
    USER_ACTIVITY = "user_activity"
    PREDICTION = "prediction"

class ActionType(Enum):
    SEND_NOTIFICATION = "send_notification"
    CREATE_TASK = "create_task"
    ADJUST_BUDGET = "adjust_budget"
    PLAY_MUSIC = "play_music"
    UPDATE_CALENDAR = "update_calendar"
    SEND_MESSAGE = "send_message"
    TRIGGER_VOICE = "trigger_voice"
    LOG_HEALTH = "log_health"

class AutomationRule:
    """Individual automation rule"""
    
    def __init__(self, rule_id: str, name: str, trigger: Dict[str, Any], 
                 actions: List[Dict[str, Any]], conditions: List[Dict[str, Any]] = None,
                 user_id: str = None, enabled: bool = True):
        self.rule_id = rule_id
        self.name = name
        self.trigger = trigger
        self.actions = actions
        self.conditions = conditions or []
        self.user_id = user_id
        self.enabled = enabled
        self.last_triggered = None
        self.trigger_count = 0

class IntelligentAutomationEngine:
    """Advanced automation system using existing NOUS features"""
    
    def __init__(self):
        """Initialize automation engine"""
        self.ai_service = UnifiedAIService()
        self.notification_service = NotificationService(db)
        self.weather_helper = WeatherHelper()
        
        # Active automation rules
        self.rules = {}
        self.active_triggers = {}
        
        # Automation history
        self.execution_history = []
        
        # Built-in automation templates
        self.templates = self._create_automation_templates()
        
        logger.info("Intelligent Automation Engine initialized")
    
    def _create_automation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create predefined automation templates"""
        return {
            'weather_based_reminders': {
                'name': 'Weather-Based Activity Reminders',
                'description': 'Automatically remind about weather-appropriate activities',
                'trigger': {
                    'type': TriggerType.WEATHER.value,
                    'condition': 'rain_probability > 70'
                },
                'actions': [
                    {
                        'type': ActionType.SEND_NOTIFICATION.value,
                        'message': 'It might rain today. Don\'t forget your umbrella!',
                        'priority': 'medium'
                    }
                ]
            },
            'morning_routine': {
                'name': 'Smart Morning Routine',
                'description': 'Automatically prepare daily briefing and tasks',
                'trigger': {
                    'type': TriggerType.TIME.value,
                    'time': '07:00',
                    'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                },
                'actions': [
                    {
                        'type': ActionType.SEND_NOTIFICATION.value,
                        'message': 'Good morning! Here\'s your daily briefing.',
                        'priority': 'high'
                    },
                    {
                        'type': ActionType.TRIGGER_VOICE.value,
                        'message': 'Ready to start your day?'
                    }
                ]
            },
            'task_completion_celebration': {
                'name': 'Task Completion Celebration',
                'description': 'Celebrate when tasks are completed',
                'trigger': {
                    'type': TriggerType.TASK_COMPLETION.value,
                    'task_type': 'any'
                },
                'actions': [
                    {
                        'type': ActionType.PLAY_MUSIC.value,
                        'playlist': 'celebration',
                        'duration': 30
                    },
                    {
                        'type': ActionType.SEND_NOTIFICATION.value,
                        'message': 'Great job completing that task!',
                        'priority': 'low'
                    }
                ]
            },
            'budget_alert': {
                'name': 'Smart Budget Monitoring',
                'description': 'Monitor spending and adjust budgets automatically',
                'trigger': {
                    'type': TriggerType.USER_ACTIVITY.value,
                    'activity': 'expense_logged',
                    'amount_threshold': 100
                },
                'actions': [
                    {
                        'type': ActionType.ADJUST_BUDGET.value,
                        'category': 'auto_detect',
                        'adjustment': 'check_limits'
                    },
                    {
                        'type': ActionType.SEND_NOTIFICATION.value,
                        'message': 'Large expense detected. Budget updated.',
                        'priority': 'medium'
                    }
                ]
            },
            'emotional_support': {
                'name': 'Emotional Support Automation',
                'description': 'Provide support based on emotional state',
                'trigger': {
                    'type': TriggerType.EMOTION.value,
                    'emotion': 'sad',
                    'confidence': 0.7
                },
                'actions': [
                    {
                        'type': ActionType.PLAY_MUSIC.value,
                        'playlist': 'uplifting',
                        'duration': 180
                    },
                    {
                        'type': ActionType.SEND_NOTIFICATION.value,
                        'message': 'I notice you might be feeling down. Would you like to talk?',
                        'priority': 'high'
                    }
                ]
            },
            'predictive_task_creation': {
                'name': 'Predictive Task Creation',
                'description': 'Create tasks based on predictions',
                'trigger': {
                    'type': TriggerType.PREDICTION.value,
                    'prediction_type': 'routine_trigger',
                    'confidence': 0.8
                },
                'actions': [
                    {
                        'type': ActionType.CREATE_TASK.value,
                        'title': 'AI-suggested task',
                        'description': 'Based on your routine patterns'
                    }
                ]
            }
        }
    
    def create_rule(self, name: str, trigger: Dict[str, Any], actions: List[Dict[str, Any]], 
                   conditions: List[Dict[str, Any]] = None, user_id: str = None) -> str:
        """Create new automation rule"""
        rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.rules)}"
        
        rule = AutomationRule(
            rule_id=rule_id,
            name=name,
            trigger=trigger,
            actions=actions,
            conditions=conditions,
            user_id=user_id
        )
        
        self.rules[rule_id] = rule
        self._register_trigger(rule)
        
        logger.info(f"Created automation rule: {name} (ID: {rule_id})")
        return rule_id
    
    def create_rule_from_template(self, template_name: str, user_id: str, 
                                 customizations: Dict[str, Any] = None) -> str:
        """Create rule from predefined template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name].copy()
        
        # Apply customizations
        if customizations:
            template.update(customizations)
        
        return self.create_rule(
            name=template['name'],
            trigger=template['trigger'],
            actions=template['actions'],
            conditions=template.get('conditions', []),
            user_id=user_id
        )
    
    def _register_trigger(self, rule: AutomationRule):
        """Register trigger for monitoring"""
        trigger_type = rule.trigger.get('type')
        
        if trigger_type not in self.active_triggers:
            self.active_triggers[trigger_type] = []
        
        self.active_triggers[trigger_type].append(rule.rule_id)
    
    async def check_triggers(self, event_data: Dict[str, Any] = None):
        """Check all active triggers and execute matching rules"""
        try:
            for trigger_type, rule_ids in self.active_triggers.items():
                for rule_id in rule_ids:
                    rule = self.rules.get(rule_id)
                    if rule and rule.enabled:
                        if await self._evaluate_trigger(rule, event_data):
                            await self._execute_rule(rule, event_data)
                            
        except Exception as e:
            logger.error(f"Error checking triggers: {e}")
    
    async def _evaluate_trigger(self, rule: AutomationRule, event_data: Dict[str, Any] = None) -> bool:
        """Evaluate if trigger condition is met"""
        trigger = rule.trigger
        trigger_type = trigger.get('type')
        
        try:
            if trigger_type == TriggerType.TIME.value:
                return self._evaluate_time_trigger(trigger)
            elif trigger_type == TriggerType.WEATHER.value:
                return await self._evaluate_weather_trigger(trigger)
            elif trigger_type == TriggerType.EMOTION.value:
                return self._evaluate_emotion_trigger(trigger, event_data)
            elif trigger_type == TriggerType.TASK_COMPLETION.value:
                return self._evaluate_task_trigger(trigger, event_data)
            elif trigger_type == TriggerType.USER_ACTIVITY.value:
                return self._evaluate_activity_trigger(trigger, event_data)
            elif trigger_type == TriggerType.PREDICTION.value:
                return self._evaluate_prediction_trigger(trigger, rule.user_id)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating trigger for rule {rule.rule_id}: {e}")
            return False
    
    def _evaluate_time_trigger(self, trigger: Dict[str, Any]) -> bool:
        """Evaluate time-based triggers"""
        now = datetime.now()
        trigger_time = trigger.get('time', '00:00')
        trigger_days = trigger.get('days', [])
        
        # Check if current day matches
        current_day = now.strftime('%A').lower()
        if trigger_days and current_day not in trigger_days:
            return False
        
        # Check if current time matches (within 1 minute window)
        try:
            hour, minute = map(int, trigger_time.split(':'))
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            time_diff = abs((now - target_time).total_seconds())
            return time_diff <= 60  # 1-minute window
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
    
    async def _evaluate_weather_trigger(self, trigger: Dict[str, Any]) -> bool:
        """Evaluate weather-based triggers"""
        try:
            condition = trigger.get('condition', '')
            weather_data = self.weather_helper.get_current_weather()
            
            if not weather_data:
                return False
            
            # Simple condition evaluation
            if 'rain_probability' in condition:
                rain_prob = weather_data.get('rain_probability', 0)
                # Extract threshold from condition string
                threshold_match = re.search(r'> (\d+)', condition)
                if threshold_match:
                    threshold = int(threshold_match.group(1))
                    return rain_prob > threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating weather trigger: {e}")
            return False
    
    def _evaluate_emotion_trigger(self, trigger: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluate emotion-based triggers"""
        if not event_data or 'emotion_data' not in event_data:
            return False
        
        emotion_data = event_data['emotion_data']
        target_emotion = trigger.get('emotion', '')
        min_confidence = trigger.get('confidence', 0.5)
        
        return (emotion_data.get('primary_emotion') == target_emotion and
                emotion_data.get('confidence', 0) >= min_confidence)
    
    def _evaluate_task_trigger(self, trigger: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluate task completion triggers"""
        if not event_data or 'task_event' not in event_data:
            return False
        
        task_event = event_data['task_event']
        trigger_task_type = trigger.get('task_type', 'any')
        
        return (task_event.get('event_type') == 'completion' and
                (trigger_task_type == 'any' or 
                 task_event.get('task_type') == trigger_task_type))
    
    def _evaluate_activity_trigger(self, trigger: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluate user activity triggers"""
        if not event_data or 'activity_data' not in event_data:
            return False
        
        activity_data = event_data['activity_data']
        target_activity = trigger.get('activity', '')
        amount_threshold = trigger.get('amount_threshold', 0)
        
        if activity_data.get('activity_type') != target_activity:
            return False
        
        if amount_threshold > 0:
            activity_amount = activity_data.get('amount', 0)
            return activity_amount >= amount_threshold
        
        return True
    
    def _evaluate_prediction_trigger(self, trigger: Dict[str, Any], user_id: str) -> bool:
        """Evaluate prediction-based triggers"""
        prediction_type = trigger.get('prediction_type', '')
        min_confidence = trigger.get('confidence', 0.5)
        
        predictions = predictive_engine.get_active_predictions(user_id)
        
        for prediction in predictions:
            if (prediction.get('type') == prediction_type and
                prediction.get('confidence', 0) >= min_confidence):
                return True
        
        return False
    
    async def _execute_rule(self, rule: AutomationRule, event_data: Dict[str, Any] = None):
        """Execute automation rule actions"""
        try:
            # Check additional conditions
            if not self._check_conditions(rule, event_data):
                return
            
            # Check cooldown period
            if self._is_in_cooldown(rule):
                return
            
            logger.info(f"Executing automation rule: {rule.name}")
            
            # Execute each action
            for action in rule.actions:
                await self._execute_action(action, rule, event_data)
            
            # Update rule execution tracking
            rule.last_triggered = datetime.now()
            rule.trigger_count += 1
            
            # Log execution
            self._log_execution(rule, event_data)
            
        except Exception as e:
            logger.error(f"Error executing rule {rule.rule_id}: {e}")
    
    def _check_conditions(self, rule: AutomationRule, event_data: Dict[str, Any]) -> bool:
        """Check additional conditions for rule execution"""
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, event_data):
                return False
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """Evaluate individual condition"""
        # Implement condition evaluation logic
        condition_type = condition.get('type', '')
        
        if condition_type == 'time_range':
            start_time = condition.get('start_time', '00:00')
            end_time = condition.get('end_time', '23:59')
            current_time = datetime.now().strftime('%H:%M')
            return start_time <= current_time <= end_time
        
        return True  # Default to true for unknown conditions
    
    def _is_in_cooldown(self, rule: AutomationRule) -> bool:
        """Check if rule is in cooldown period"""
        if not rule.last_triggered:
            return False
        
        # Default cooldown of 1 hour
        cooldown_minutes = 60
        cooldown_end = rule.last_triggered + timedelta(minutes=cooldown_minutes)
        
        return datetime.now() < cooldown_end
    
    async def _execute_action(self, action: Dict[str, Any], rule: AutomationRule, 
                            event_data: Dict[str, Any] = None):
        """Execute individual action"""
        action_type = action.get('type')
        
        try:
            if action_type == ActionType.SEND_NOTIFICATION.value:
                await self._action_send_notification(action, rule)
            elif action_type == ActionType.CREATE_TASK.value:
                await self._action_create_task(action, rule)
            elif action_type == ActionType.PLAY_MUSIC.value:
                await self._action_play_music(action, rule)
            elif action_type == ActionType.TRIGGER_VOICE.value:
                await self._action_trigger_voice(action, rule)
            elif action_type == ActionType.ADJUST_BUDGET.value:
                await self._action_adjust_budget(action, rule)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
    
    async def _action_send_notification(self, action: Dict[str, Any], rule: AutomationRule):
        """Send notification action"""
        message = action.get('message', 'Automation triggered')
        priority = action.get('priority', 'medium')
        
        self.notification_service.send_notification(
            user_id=rule.user_id,
            title=f"Automation: {rule.name}",
            message=message,
            priority=priority,
            category="automation"
        )
    
    async def _action_create_task(self, action: Dict[str, Any], rule: AutomationRule):
        """Create task action"""
        title = action.get('title', 'Automated Task')
        description = action.get('description', f'Created by automation rule: {rule.name}')
        
        # This would integrate with your task management system
        logger.info(f"Creating automated task: {title}")
    
    async def _action_play_music(self, action: Dict[str, Any], rule: AutomationRule):
        """Play music action"""
        playlist = action.get('playlist', 'default')
        duration = action.get('duration', 60)
        
        # This would integrate with your Spotify service
        logger.info(f"Playing music playlist: {playlist} for {duration} seconds")
    
    async def _action_trigger_voice(self, action: Dict[str, Any], rule: AutomationRule):
        """Trigger voice response action"""
        message = action.get('message', 'Automation triggered')
        
        # This would integrate with your enhanced voice interface
        logger.info(f"Voice trigger: {message}")
    
    async def _action_adjust_budget(self, action: Dict[str, Any], rule: AutomationRule):
        """Adjust budget action"""
        category = action.get('category', 'miscellaneous')
        adjustment = action.get('adjustment', 'check_limits')
        
        # This would integrate with your financial management system
        logger.info(f"Budget adjustment: {adjustment} for category {category}")
    
    def _log_execution(self, rule: AutomationRule, event_data: Dict[str, Any]):
        """Log rule execution"""
        execution_log = {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'timestamp': datetime.now().isoformat(),
            'trigger_data': event_data,
            'user_id': rule.user_id
        }
        
        self.execution_history.append(execution_log)
        
        # Keep last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history.pop(0)
    
    def get_user_rules(self, user_id: str) -> List[Dict[str, Any]]:
        """Get automation rules for specific user"""
        user_rules = []
        for rule in self.rules.values():
            if rule.user_id == user_id:
                user_rules.append({
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'enabled': rule.enabled,
                    'trigger': rule.trigger,
                    'actions': rule.actions,
                    'last_triggered': rule.last_triggered,
                    'trigger_count': rule.trigger_count
                })
        return user_rules
    
    def enable_rule(self, rule_id: str):
        """Enable automation rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Enabled automation rule: {rule_id}")
    
    def disable_rule(self, rule_id: str):
        """Disable automation rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Disabled automation rule: {rule_id}")
    
    def delete_rule(self, rule_id: str):
        """Delete automation rule"""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            del self.rules[rule_id]
            
            # Remove from active triggers
            for trigger_type, rule_ids in self.active_triggers.items():
                if rule_id in rule_ids:
                    rule_ids.remove(rule_id)
            
            logger.info(f"Deleted automation rule: {rule.name}")
    
    def get_execution_history(self, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get automation execution history"""
        history = self.execution_history
        
        if user_id:
            history = [log for log in history if log.get('user_id') == user_id]
        
        return history[-limit:] if limit else history
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available automation templates"""
        return self.templates
    
    async def trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Manually trigger event for testing automation"""
        await self.check_triggers({
            'event_type': event_type,
            **event_data
        })

# Global instance
automation_engine = IntelligentAutomationEngine()