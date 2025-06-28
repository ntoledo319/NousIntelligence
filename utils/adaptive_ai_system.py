"""
Adaptive AI System - Enhanced Learning Architecture
Incorporates experience replay, multi-agent coordination, and dynamic resource optimization
Based on advanced ML concepts for continuous improvement and personalization
"""

import os
import time
import json
import psutil
import numpy as np
import asyncio
import random
import logging
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions the AI can take"""
    TASK_CREATION = 0
    CONTEXT_SWITCH = 1
    RESOURCE_OPTIMIZATION = 2
    LEARNING_UPDATE = 3
    USER_ASSISTANCE = 4

class RewardType(Enum):
    """Types of rewards for learning"""
    USER_SATISFACTION = "user_satisfaction"
    TASK_COMPLETION = "task_completion"
    RESPONSE_TIME = "response_time"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    ACCURACY = "accuracy"

@dataclass
class Experience:
    """Represents a learning experience"""
    timestamp: float
    user_context: Dict[str, Any]
    action_taken: int
    reward: float
    outcome_state: Dict[str, Any]
    user_feedback: Optional[float] = None
    session_id: str = ""
    task_type: str = ""

@dataclass
class UserProfile:
    """User behavior and preference profile"""
    user_id: str
    interaction_patterns: Dict[str, Any]
    preference_weights: Dict[str, float]
    learning_rate: float = 0.1
    last_updated: Optional[datetime] = None

class DynamicResourceManager:
    """Intelligent resource allocation based on system state and user needs"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count(logical=True)
        self.total_memory = psutil.virtual_memory().total
        self.load_history = deque(maxlen=100)
        self.optimization_factor = 0.85  # Conservative by default
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'available_memory': memory.available,
            'disk_usage': disk.percent,
            'load_avg': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
        }
        
        self.load_history.append(metrics)
        return metrics
    
    def calculate_optimal_resources(self, task_complexity: int = 1) -> Tuple[int, int]:
        """Calculate optimal thread and process counts based on current load"""
        metrics = self.get_system_metrics()
        
        # Adjust based on current system load
        cpu_factor = max(0.3, 1.0 - (metrics['cpu_usage'] / 100.0))
        memory_factor = max(0.3, 1.0 - (metrics['memory_usage'] / 100.0))
        
        # Calculate optimal thread count
        base_threads = max(2, int(self.cpu_count * self.optimization_factor))
        optimal_threads = max(1, int(base_threads * cpu_factor * task_complexity))
        
        # Calculate optimal process count (more conservative)
        process_memory_limit = 256 * 1024 * 1024  # 256MB per process
        max_processes_by_memory = max(1, int(metrics['available_memory'] / process_memory_limit))
        optimal_processes = min(max_processes_by_memory, max(1, int(self.cpu_count * memory_factor)))
        
        return min(optimal_threads, 16), min(optimal_processes, 4)  # Cap at reasonable limits

class ExperienceReplaySystem:
    """Advanced experience replay with prioritization and user-specific learning"""
    
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.experiences = deque(maxlen=capacity)
        self.user_experiences = defaultdict(lambda: deque(maxlen=1000))
        self.priority_weights = {
            RewardType.USER_SATISFACTION: 2.0,
            RewardType.TASK_COMPLETION: 1.5,
            RewardType.RESPONSE_TIME: 1.0,
            RewardType.RESOURCE_EFFICIENCY: 0.8,
            RewardType.ACCURACY: 1.8
        }
    
    def store_experience(self, experience: Experience):
        """Store a new learning experience"""
        self.experiences.append(experience)
        if experience.user_context.get('user_id'):
            user_id = experience.user_context['user_id']
            self.user_experiences[user_id].append(experience)
        
        logger.debug(f"Stored experience: action={experience.action_taken}, reward={experience.reward}")
    
    def sample_experiences(self, batch_size: int = 32, user_id: Optional[str] = None) -> List[Experience]:
        """Sample experiences with prioritization"""
        if user_id and user_id in self.user_experiences:
            # Prioritize user-specific experiences (70%) + global experiences (30%)
            user_sample_size = int(batch_size * 0.7)
            global_sample_size = batch_size - user_sample_size
            
            user_experiences = list(self.user_experiences[user_id])
            global_experiences = [exp for exp in self.experiences if exp.user_context.get('user_id') != user_id]
            
            # Sample from user experiences with reward-based prioritization
            user_sample = self._prioritized_sample(user_experiences, user_sample_size)
            global_sample = self._prioritized_sample(global_experiences, global_sample_size)
            
            return user_sample + global_sample
        else:
            # Sample globally with prioritization
            return self._prioritized_sample(list(self.experiences), batch_size)
    
    def _prioritized_sample(self, experiences: List[Experience], sample_size: int) -> List[Experience]:
        """Sample experiences based on reward priority"""
        if not experiences or sample_size <= 0:
            return []
        
        sample_size = min(sample_size, len(experiences))
        
        # Sort by reward (prioritize high-reward experiences)
        sorted_experiences = sorted(experiences, key=lambda x: x.reward, reverse=True)
        
        # Take top 50% deterministically, sample remaining 50% randomly
        top_count = max(1, sample_size // 2)
        random_count = sample_size - top_count
        
        result = sorted_experiences[:top_count]
        
        if random_count > 0 and len(sorted_experiences) > top_count:
            remaining = sorted_experiences[top_count:]
            result.extend(random.sample(remaining, min(random_count, len(remaining))))
        
        return result

class MultiAgentCoordinator:
    """Coordinates multiple AI agents for different aspects of personal assistance"""
    
    def __init__(self, num_agents: int = 4):
        self.agents = {
            'task_agent': {'specialization': 'task_management', 'performance': 1.0},
            'context_agent': {'specialization': 'context_understanding', 'performance': 1.0},
            'optimization_agent': {'specialization': 'resource_optimization', 'performance': 1.0},
            'learning_agent': {'specialization': 'user_learning', 'performance': 1.0}
        }
        self.agent_performance_history = defaultdict(list)
        self.coordination_weights = {agent: 1.0 for agent in self.agents.keys()}
    
    def select_agent_for_task(self, task_type: str, context: Dict[str, Any]) -> str:
        """Select the best agent for a given task"""
        # Match task type to agent specialization
        task_mapping = {
            'task_creation': 'task_agent',
            'context_analysis': 'context_agent',
            'optimization': 'optimization_agent',
            'learning': 'learning_agent'
        }
        
        preferred_agent = task_mapping.get(task_type, 'task_agent')
        
        # Consider agent performance history
        if preferred_agent in self.agent_performance_history:
            recent_performance = self.agent_performance_history[preferred_agent][-10:]
            if recent_performance and np.mean(recent_performance) < 0.7:
                # If preferred agent is underperforming, select best performing alternative
                best_agent = max(self.agents.keys(), 
                               key=lambda a: np.mean(self.agent_performance_history.get(a, [1.0])[-10:]))
                return best_agent
        
        return preferred_agent
    
    def update_agent_performance(self, agent_id: str, performance_score: float):
        """Update agent performance tracking"""
        self.agent_performance_history[agent_id].append(performance_score)
        self.agents[agent_id]['performance'] = np.mean(self.agent_performance_history[agent_id][-20:])

class AdaptiveAISystem:
    """Main adaptive AI system that learns and improves over time"""
    
    def __init__(self):
        self.resource_manager = DynamicResourceManager()
        self.experience_replay = ExperienceReplaySystem()
        self.multi_agent = MultiAgentCoordinator()
        self.user_profiles = {}
        
        # Learning parameters
        self.learning_rate = 0.01
        self.exploration_rate = 0.15
        self.exploration_decay = 0.995
        self.min_exploration = 0.05
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
        self.last_optimization = time.time()
        self.optimization_interval = 300  # 5 minutes
        
        # Task execution
        self.thread_executor = None
        self.process_executor = None
        self._initialize_executors()
    
    def _initialize_executors(self):
        """Initialize thread and process executors with optimal configuration"""
        max_threads, max_processes = self.resource_manager.calculate_optimal_resources()
        
        if self.thread_executor:
            self.thread_executor.shutdown(wait=False)
        if self.process_executor:
            self.process_executor.shutdown(wait=False)
        
        self.thread_executor = ThreadPoolExecutor(max_workers=max_threads)
        self.process_executor = ProcessPoolExecutor(max_workers=max_processes)
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                interaction_patterns={},
                preference_weights={reward_type.value: 1.0 for reward_type in RewardType},
                last_updated=datetime.now()
            )
        return self.user_profiles[user_id]
    
    def process_user_request(self, user_id: str, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user request using adaptive AI approach"""
        start_time = time.time()
        user_profile = self.get_user_profile(user_id)
        
        # Determine request complexity and select appropriate agent
        task_complexity = self._analyze_request_complexity(request, context)
        agent_id = self.multi_agent.select_agent_for_task(task_complexity['type'], context)
        
        # Choose action based on exploration vs exploitation
        action = self._select_action(user_profile, context, task_complexity)
        
        # Execute action
        result = self._execute_action(action, request, context, user_profile)
        
        # Calculate reward based on multiple factors
        processing_time = time.time() - start_time
        reward = self._calculate_reward(result, processing_time, user_profile)
        
        # Store experience for learning
        experience = Experience(
            timestamp=start_time,
            user_context={**context, 'user_id': user_id},
            action_taken=action,
            reward=reward,
            outcome_state=result,
            session_id=context.get('session_id', ''),
            task_type=task_complexity['type']
        )
        self.experience_replay.store_experience(experience)
        
        # Update performance metrics
        self.performance_metrics['response_time'].append(processing_time)
        self.performance_metrics['reward'].append(reward)
        
        # Periodic optimization
        if time.time() - self.last_optimization > self.optimization_interval:
            self._optimize_system()
        
        return {
            'result': result,
            'processing_time': processing_time,
            'agent_used': agent_id,
            'reward': reward,
            'learning_update': True
        }
    
    def _analyze_request_complexity(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request complexity to determine processing approach"""
        # Simple heuristics for complexity analysis
        word_count = len(request.split())
        has_context = len(context) > 2
        
        if word_count < 10 and not has_context:
            return {'type': 'simple', 'complexity': 1}
        elif word_count < 50:
            return {'type': 'standard', 'complexity': 2}
        else:
            return {'type': 'complex', 'complexity': 3}
    
    def _select_action(self, user_profile: UserProfile, context: Dict[str, Any], task_complexity: Dict[str, Any]) -> int:
        """Select action using exploration vs exploitation strategy"""
        if random.random() < self.exploration_rate:
            # Exploration: try random action
            return random.randint(0, len(ActionType) - 1)
        else:
            # Exploitation: use learned preferences
            # Simple heuristic based on user profile and context
            if task_complexity['complexity'] == 1:
                return ActionType.USER_ASSISTANCE.value
            elif task_complexity['complexity'] == 2:
                return ActionType.TASK_CREATION.value
            else:
                return ActionType.CONTEXT_SWITCH.value
    
    def _execute_action(self, action: int, request: str, context: Dict[str, Any], user_profile: UserProfile) -> Dict[str, Any]:
        """Execute the selected action"""
        action_type = ActionType(action)
        
        result = {
            'action_type': action_type.name,
            'success': True,
            'message': f"Executed {action_type.name} for request: {request[:50]}...",
            'timestamp': datetime.now().isoformat()
        }
        
        # Add action-specific processing
        if action_type == ActionType.TASK_CREATION:
            result['tasks_created'] = self._create_tasks_from_request(request, context)
        elif action_type == ActionType.CONTEXT_SWITCH:
            result['context_update'] = self._update_context(context, user_profile)
        elif action_type == ActionType.RESOURCE_OPTIMIZATION:
            result['optimization'] = self._optimize_resources()
        elif action_type == ActionType.LEARNING_UPDATE:
            result['learning'] = self._update_learning(user_profile)
        
        return result
    
    def _create_tasks_from_request(self, request: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create tasks from user request"""
        # Simplified task creation logic
        return [
            {
                'title': f"Task derived from: {request[:30]}...",
                'priority': 'medium',
                'estimated_duration': '30 minutes'
            }
        ]
    
    def _update_context(self, context: Dict[str, Any], user_profile: UserProfile) -> Dict[str, Any]:
        """Update context based on user profile"""
        return {
            'context_enhanced': True,
            'user_preferences_applied': len(user_profile.preference_weights),
            'context_size': len(context)
        }
    
    def _optimize_resources(self) -> Dict[str, Any]:
        """Optimize system resources"""
        metrics = self.resource_manager.get_system_metrics()
        max_threads, max_processes = self.resource_manager.calculate_optimal_resources()
        
        return {
            'current_metrics': metrics,
            'recommended_threads': max_threads,
            'recommended_processes': max_processes
        }
    
    def _update_learning(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Update learning based on recent experiences"""
        recent_experiences = self.experience_replay.sample_experiences(
            batch_size=10, 
            user_id=user_profile.user_id
        )
        
        if recent_experiences:
            avg_reward = np.mean([exp.reward for exp in recent_experiences])
            user_profile.last_updated = datetime.now()
            
            return {
                'experiences_analyzed': len(recent_experiences),
                'average_reward': avg_reward,
                'learning_rate': user_profile.learning_rate
            }
        
        return {'learning_update': 'no_recent_experiences'}
    
    def _calculate_reward(self, result: Dict[str, Any], processing_time: float, user_profile: UserProfile) -> float:
        """Calculate reward based on multiple factors"""
        base_reward = 1.0 if result.get('success', False) else 0.0
        
        # Time penalty (prefer faster responses)
        time_factor = max(0.1, 1.0 - (processing_time / 10.0))  # Penalty after 10 seconds
        
        # Success bonus
        success_bonus = 0.5 if result.get('success', False) else -0.5
        
        # User preference alignment (simplified)
        preference_bonus = 0.2 if len(result) > 3 else 0.0  # More detailed results preferred
        
        total_reward = base_reward * time_factor + success_bonus + preference_bonus
        
        # Apply exploration decay
        self.exploration_rate = max(self.min_exploration, self.exploration_rate * self.exploration_decay)
        
        return max(-1.0, min(2.0, total_reward))  # Clamp between -1 and 2
    
    def _optimize_system(self):
        """Periodic system optimization"""
        self.last_optimization = time.time()
        
        # Re-initialize executors with current optimal configuration
        self._initialize_executors()
        
        # Update multi-agent performance
        if self.performance_metrics['reward']:
            recent_performance = float(np.mean(self.performance_metrics['reward'][-50:]))
            for agent_id in self.multi_agent.agents.keys():
                self.multi_agent.update_agent_performance(agent_id, recent_performance)
        
        logger.info("System optimization completed")
    
    def get_learning_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get insights about the learning system"""
        insights = {
            'total_experiences': len(self.experience_replay.experiences),
            'exploration_rate': self.exploration_rate,
            'avg_response_time': np.mean(self.performance_metrics['response_time'][-100:]) if self.performance_metrics['response_time'] else 0,
            'avg_reward': np.mean(self.performance_metrics['reward'][-100:]) if self.performance_metrics['reward'] else 0,
            'system_metrics': self.resource_manager.get_system_metrics()
        }
        
        if user_id and user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            insights['user_profile'] = {
                'learning_rate': profile.learning_rate,
                'last_updated': profile.last_updated.isoformat() if profile.last_updated else None,
                'preference_weights': profile.preference_weights
            }
        
        return insights
    
    def update_from_user_feedback(self, user_id: str, feedback_score: float, session_context: Dict[str, Any]):
        """Update learning based on explicit user feedback"""
        # Find recent experiences for this user
        recent_experiences = [
            exp for exp in list(self.experience_replay.experiences)[-20:]
            if exp.user_context.get('user_id') == user_id
        ]
        
        if recent_experiences:
            # Update the most recent experience with user feedback
            latest_experience = recent_experiences[-1]
            latest_experience.user_feedback = feedback_score
            
            # Adjust user profile based on feedback
            user_profile = self.get_user_profile(user_id)
            if feedback_score > 0.7:  # Positive feedback
                user_profile.learning_rate = min(0.2, user_profile.learning_rate * 1.1)
            elif feedback_score < 0.3:  # Negative feedback
                user_profile.learning_rate = max(0.01, user_profile.learning_rate * 0.9)
            
            logger.info(f"Updated learning from user feedback: {feedback_score}")

# Global adaptive AI system instance
adaptive_ai = None

def get_adaptive_ai() -> AdaptiveAISystem:
    """Get or create the global adaptive AI system"""
    global adaptive_ai
    if adaptive_ai is None:
        adaptive_ai = AdaptiveAISystem()
    return adaptive_ai

def process_adaptive_request(user_id: str, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process a request using the adaptive AI system"""
    if context is None:
        context = {}
    
    ai_system = get_adaptive_ai()
    return ai_system.process_user_request(user_id, request, context)

def provide_user_feedback(user_id: str, feedback_score: float, session_context: Optional[Dict[str, Any]] = None):
    """Provide user feedback to improve the AI system"""
    if session_context is None:
        session_context = {}
    
    ai_system = get_adaptive_ai()
    ai_system.update_from_user_feedback(user_id, feedback_score, session_context)

def get_ai_insights(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get insights about the AI learning system"""
    ai_system = get_adaptive_ai()
    return ai_system.get_learning_insights(user_id)