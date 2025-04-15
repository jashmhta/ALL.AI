import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime

class ModelOptimizer:
    """
    Optimizes model selection and parameters based on performance data.
    Analyzes response quality, latency, and cost to recommend optimal models.
    """
    
    def __init__(self):
        """Initialize the model optimizer."""
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "optimization")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize performance data
        self.performance_data = self._load_performance_data()
    
    def _load_performance_data(self) -> Dict[str, Any]:
        """
        Load performance data from storage.
        
        Returns:
            Dict containing performance data
        """
        filepath = os.path.join(self.storage_dir, "performance_data.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading performance data: {e}")
                return self._initialize_performance_data()
        else:
            return self._initialize_performance_data()
    
    def _initialize_performance_data(self) -> Dict[str, Any]:
        """
        Initialize empty performance data structure.
        
        Returns:
            Dict containing empty performance data
        """
        return {
            "models": {},
            "requests": [],
            "optimizations": []
        }
    
    def _save_performance_data(self) -> bool:
        """
        Save performance data to storage.
        
        Returns:
            True if saving was successful, False otherwise
        """
        filepath = os.path.join(self.storage_dir, "performance_data.json")
        
        try:
            with open(filepath, "w") as f:
                json.dump(self.performance_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving performance data: {e}")
            return False
    
    def record_request(self, model: str, prompt: str, response: Dict[str, Any], 
                      latency: float, tokens: Dict[str, int], 
                      conversation_id: Optional[str] = None) -> bool:
        """
        Record a model request and its performance metrics.
        
        Args:
            model: The model that was used
            prompt: The prompt that was sent
            response: The response that was received
            latency: Request latency in seconds
            tokens: Dict with prompt_tokens, completion_tokens, and total_tokens
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if recording was successful, False otherwise
        """
        try:
            # Initialize model data if it doesn't exist
            if model not in self.performance_data["models"]:
                self.performance_data["models"][model] = {
                    "requests": 0,
                    "total_latency": 0,
                    "avg_latency": 0,
                    "total_tokens": 0,
                    "avg_tokens_per_request": 0,
                    "success_rate": 100.0,
                    "failures": 0
                }
            
            # Create request entry
            success = response.get("success", False)
            
            request_entry = {
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conversation_id,
                "latency": latency,
                "tokens": tokens,
                "success": success,
                "prompt_length": len(prompt)
            }
            
            # Add to requests list
            self.performance_data["requests"].append(request_entry)
            
            # Update model performance data
            model_data = self.performance_data["models"][model]
            model_data["requests"] += 1
            
            if success:
                model_data["total_latency"] += latency
                model_data["avg_latency"] = model_data["total_latency"] / (model_data["requests"] - model_data["failures"])
                
                total_tokens = tokens.get("total_tokens", 0)
                model_data["total_tokens"] += total_tokens
                model_data["avg_tokens_per_request"] = model_data["total_tokens"] / (model_data["requests"] - model_data["failures"])
            else:
                model_data["failures"] += 1
            
            model_data["success_rate"] = ((model_data["requests"] - model_data["failures"]) / model_data["requests"]) * 100
            
            # Save performance data
            return self._save_performance_data()
        except Exception as e:
            print(f"Error recording request: {e}")
            return False
    
    def get_model_performance(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance data for a specific model or all models.
        
        Args:
            model: The model to get performance data for, or None for all models
            
        Returns:
            Dict containing performance data
        """
        if model:
            return self.performance_data["models"].get(model, {
                "requests": 0,
                "total_latency": 0,
                "avg_latency": 0,
                "total_tokens": 0,
                "avg_tokens_per_request": 0,
                "success_rate": 0,
                "failures": 0
            })
        else:
            return {
                "models": self.performance_data["models"],
                "total_requests": len(self.performance_data["requests"])
            }
    
    def recommend_model(self, prompt: str, priority: str = "balanced") -> Dict[str, Any]:
        """
        Recommend the best model for a given prompt based on performance data.
        
        Args:
            prompt: The prompt to be processed
            priority: Optimization priority (speed, quality, cost, or balanced)
            
        Returns:
            Dict containing the recommended model and parameters
        """
        try:
            # Get available models
            models = self.performance_data["models"]
            
            if not models:
                return {
                    "model": None,
                    "parameters": {},
                    "reason": "No performance data available for any model"
                }
            
            # Calculate prompt complexity
            prompt_length = len(prompt)
            prompt_complexity = self._calculate_prompt_complexity(prompt)
            
            # Score models based on priority
            model_scores = {}
            
            for model_name, model_data in models.items():
                if model_data["requests"] < 5:
                    # Not enough data for reliable recommendation
                    continue
                
                # Calculate base scores (0-100 scale)
                speed_score = 100 - min(100, (model_data["avg_latency"] / 10) * 100)  # Lower latency is better
                quality_score = model_data["success_rate"]  # Higher success rate is better
                efficiency_score = 100 - min(100, (model_data["avg_tokens_per_request"] / 2000) * 100)  # Lower token usage is better
                
                # Adjust for prompt complexity
                if prompt_complexity > 0.7:  # High complexity
                    quality_score *= 1.2  # Boost quality importance
                    speed_score *= 0.8  # Reduce speed importance
                elif prompt_complexity < 0.3:  # Low complexity
                    quality_score *= 0.9  # Reduce quality importance
                    speed_score *= 1.1  # Boost speed importance
                
                # Calculate weighted score based on priority
                if priority == "speed":
                    final_score = speed_score * 0.7 + quality_score * 0.2 + efficiency_score * 0.1
                elif priority == "quality":
                    final_score = quality_score * 0.7 + speed_score * 0.1 + efficiency_score * 0.2
                elif priority == "cost":
                    final_score = efficiency_score * 0.7 + speed_score * 0.2 + quality_score * 0.1
                else:  # balanced
                    final_score = speed_score * 0.33 + quality_score * 0.34 + efficiency_score * 0.33
                
                model_scores[model_name] = {
                    "final_score": final_score,
                    "speed_score": speed_score,
                    "quality_score": quality_score,
                    "efficiency_score": efficiency_score
                }
            
            if not model_scores:
                return {
                    "model": None,
                    "parameters": {},
                    "reason": "Not enough performance data for reliable recommendations"
                }
            
            # Find the best model
            best_model = max(model_scores.items(), key=lambda x: x[1]["final_score"])
            model_name = best_model[0]
            scores = best_model[1]
            
            # Determine optimal parameters based on prompt complexity
            parameters = self._get_optimal_parameters(model_name, prompt_complexity, priority)
            
            # Create recommendation entry
            recommendation = {
                "timestamp": datetime.now().isoformat(),
                "prompt_length": prompt_length,
                "prompt_complexity": prompt_complexity,
                "priority": priority,
                "recommended_model": model_name,
                "scores": scores,
                "parameters": parameters
            }
            
            # Add to optimizations list
            self.performance_data["optimizations"].append(recommendation)
            self._save_performance_data()
            
            return {
                "model": model_name,
                "parameters": parameters,
                "scores": scores,
                "reason": f"Best {priority} performance for prompt complexity {prompt_complexity:.2f}"
            }
        except Exception as e:
            print(f"Error recommending model: {e}")
            return {
                "model": None,
                "parameters": {},
                "reason": f"Error during recommendation: {str(e)}"
            }
    
    def _calculate_prompt_complexity(self, prompt: str) -> float:
        """
        Calculate the complexity of a prompt (0.0 to 1.0 scale).
        
        Args:
            prompt: The prompt to analyze
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Simple complexity calculation based on length, sentence structure, and special characters
        length_factor = min(1.0, len(prompt) / 1000)  # Length up to 1000 chars
        
        # Count sentences
        sentences = prompt.split('.')
        sentence_count = len([s for s in sentences if len(s.strip()) > 0])
        sentence_factor = min(1.0, sentence_count / 20)  # Up to 20 sentences
        
        # Count special characters (code indicators)
        code_indicators = sum(1 for c in prompt if c in '{}[]()=+-*/><')
        code_factor = min(1.0, code_indicators / 100)  # Up to 100 special chars
        
        # Calculate weighted complexity
        complexity = (length_factor * 0.4) + (sentence_factor * 0.3) + (code_factor * 0.3)
        
        return complexity
    
    def _get_optimal_parameters(self, model: str, complexity: float, priority: str) -> Dict[str, Any]:
        """
        Get optimal parameters for a model based on prompt complexity and priority.
        
        Args:
            model: The model to get parameters for
            complexity: Prompt complexity score (0.0 to 1.0)
            priority: Optimization priority
            
        Returns:
            Dict containing optimal parameters
        """
        # Base parameters
        parameters = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9
        }
        
        # Adjust based on complexity and priority
        if priority == "speed":
            parameters["temperature"] = 0.5  # Lower temperature for faster responses
            parameters["max_tokens"] = int(500 + (complexity * 500))  # 500-1000 based on complexity
        elif priority == "quality":
            parameters["temperature"] = 0.3 + (complexity * 0.4)  # 0.3-0.7 based on complexity
            parameters["max_tokens"] = int(1000 + (complexity * 1000))  # 1000-2000 based on complexity
            parameters["top_p"] = 0.95  # Higher top_p for better quality
        elif priority == "cost":
            parameters["temperature"] = 0.7  # Standard temperature
            parameters["max_tokens"] = int(300 + (complexity * 700))  # 300-1000 based on complexity
        else:  # balanced
            parameters["temperature"] = 0.5 + (complexity * 0.3)  # 0.5-0.8 based on complexity
            parameters["max_tokens"] = int(800 + (complexity * 700))  # 800-1500 based on complexity
        
        return parameters
    
    def generate_performance_chart(self) -> Optional[str]:
        """
        Generate a chart of model performance metrics.
        
        Returns:
            Base64-encoded PNG image of the chart, or None if generation failed
        """
        try:
            # Get model data
            models = self.performance_data["models"]
            
            if not models:
                return None
            
            # Prepare data for chart
            model_names = []
            avg_latencies = []
            success_rates = []
            avg_tokens = []
            
            for model, data in models.items():
                if data["requests"] > 0:
                    model_names.append(model)
                    avg_latencies.append(data["avg_latency"])
                    success_rates.append(data["success_rate"])
                    avg_tokens.append(data["avg_tokens_per_request"])
            
            if not model_names:
                return None
            
            # Create figure with three subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
            
            # Plot average latencies
            bars = ax1.bar(model_names, avg_latencies, color='skyblue')
            ax1.set_title('Average Latency by Model')
            ax1.set_xlabel('Model')
            ax1.set_ylabel('Latency (seconds)')
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.2f}s', ha='center', va='bottom')
            
            # Plot success rates
            bars = ax2.bar(model_names, success_rates, color='lightgreen')
            ax2.set_title('Success Rate by Model')
            ax2.set_xlabel('Model')
            ax2.set_ylabel('Success Rate (%)')
            ax2.set_ylim(0, 105)
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
            
            # Plot average tokens p
(Content truncated due to size limit. Use line ranges to read in chunks)