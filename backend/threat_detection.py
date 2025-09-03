import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List
from transformers import pipeline
import torch
#from emergentintegrations.llm.chat import LlmChat, UserMessage   
from dotenv import load_dotenv
import imagehash
from PIL import Image
import requests
from io import BytesIO

load_dotenv()


class ThreatDetectionEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # HuggingFace Models
        self.toxic_classifier = None
        self.sentiment_analyzer = None

        # LLM Chat for advanced analysis (disabled placeholder)
        self.llm_chat = None

        # Official image hashes for comparison (placeholder)
        self.official_image_hashes = set()

    async def initialize(self):
        """Initialize all models and components"""
        try:
            self.logger.info("Initializing threat detection models...")

            # Initialize HuggingFace models
            await self._initialize_huggingface_models()

            # Skip LLM initialization since module is missing
            self.llm_chat = None

            # Load official image hashes
            self._load_official_image_hashes()

            self.logger.info("Threat detection engine initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize threat detection engine: {e}")
            raise

    async def _initialize_huggingface_models(self):
        """Initialize HuggingFace models for toxicity and sentiment analysis"""
        try:
            self.toxic_classifier = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=0 if self.device == "cuda" else -1
            )

            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device == "cuda" else -1
            )

            self.logger.info("HuggingFace models loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize HuggingFace models: {e}")
            # fallback
            self.toxic_classifier = self._mock_toxic_classifier
            self.sentiment_analyzer = self._mock_sentiment_analyzer

    def _load_official_image_hashes(self):
        """Load official image hashes for misuse detection"""
        placeholder_hashes = [
            "a1b2c3d4e5f6g7h8",  # Example hash
            "h8g7f6e5d4c3b2a1",  # Example hash
        ]
        self.official_image_hashes = set(placeholder_hashes)
        self.logger.info(f"Loaded {len(self.official_image_hashes)} official image hashes")

    async def analyze_post(self, content: str, author: str, platform: str,
                           post_url: str = "", image_urls: List[str] = None) -> Dict:
        """Comprehensive threat analysis of a social media post"""
        try:
            analysis_results = {
                "is_threat": False,
                "threat_level": "low",
                "reasons": [],
                "scores": {},
                "ai_analysis": "",
                "overall_score": 0.0
            }

            # Toxicity
            toxicity_result = await self._analyze_toxicity(content)
            analysis_results["scores"]["toxicity"] = toxicity_result["score"]

            if toxicity_result["is_toxic"]:
                analysis_results["is_threat"] = True
                analysis_results["reasons"].append("Violence & Threat Detection")

            # Sentiment
            sentiment_result = await self._analyze_sentiment(content)
            analysis_results["scores"]["sentiment"] = sentiment_result["score"]

            if sentiment_result["is_negative"]:
                analysis_results["reasons"].append("Negative Sentiment")

            # Fake account
            fake_account_result = await self._analyze_fake_account(author, platform)
            analysis_results["scores"]["fake_account"] = fake_account_result["score"]

            if fake_account_result["is_suspicious"]:
                analysis_results["reasons"].append("Suspicious Account")

            # Image misuse
            if image_urls:
                image_result = await self._analyze_image_misuse(image_urls)
                analysis_results["scores"]["image_misuse"] = image_result["score"]

                if image_result["is_misuse"]:
                    analysis_results["reasons"].append("Image Misuse")

            # LLM Analysis (disabled)
            analysis_results["ai_analysis"] = "LLM analysis unavailable"
            analysis_results["scores"]["llm_confidence"] = 0.0

            # Overall threat score
            analysis_results["overall_score"] = self._calculate_overall_score(
                analysis_results["scores"]
            )

            # Final level
            if analysis_results["overall_score"] >= 0.8:
                analysis_results["threat_level"] = "critical"
            elif analysis_results["overall_score"] >= 0.6:
                analysis_results["threat_level"] = "high"
            elif analysis_results["overall_score"] >= 0.4:
                analysis_results["threat_level"] = "medium"
            else:
                analysis_results["threat_level"] = "low"

            return analysis_results

        except Exception as e:
            self.logger.error(f"Error analyzing post: {e}")
            return {
                "is_threat": False,
                "threat_level": "low",
                "reasons": ["Analysis Error"],
                "scores": {},
                "ai_analysis": f"Error during analysis: {str(e)}",
                "overall_score": 0.0
            }

    async def _analyze_toxicity(self, content: str) -> Dict:
        try:
            result = self.toxic_classifier(content) if callable(self.toxic_classifier) else [
                {"label": "TOXIC", "score": 0.3}
            ]

            is_toxic = result[0]["label"] == "TOXIC" and result[0]["score"] > 0.7

            return {
                "is_toxic": is_toxic,
                "score": result[0]["score"] if result[0]["label"] == "TOXIC" else 1 - result[0]["score"],
                "label": result[0]["label"]
            }

        except Exception as e:
            self.logger.error(f"Toxicity analysis error: {e}")
            return {"is_toxic": False, "score": 0.0, "label": "ERROR"}

    async def _analyze_sentiment(self, content: str) -> Dict:
        try:
            result = self.sentiment_analyzer(content) if callable(self.sentiment_analyzer) else [
                {"label": "NEGATIVE", "score": 0.4}
            ]

            is_negative = result[0]["label"] == "NEGATIVE" and result[0]["score"] > 0.6

            return {
                "is_negative": is_negative,
                "score": result[0]["score"],
                "label": result[0]["label"]
            }

        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {e}")
            return {"is_negative": False, "score": 0.0, "label": "ERROR"}

    async def _analyze_fake_account(self, author: str, platform: str) -> Dict:
        try:
            suspicious_patterns = [
                "bot", "fake", "spam", "_123", "random", "temp",
                "user123", "account123", "profile123"
            ]
            is_suspicious = any(pattern in author.lower() for pattern in suspicious_patterns)
            score = 0.8 if is_suspicious else 0.2

            return {
                "is_suspicious": is_suspicious,
                "score": score,
                "reasons": ["Suspicious username pattern"] if is_suspicious else []
            }

        except Exception as e:
            self.logger.error(f"Fake account analysis error: {e}")
            return {"is_suspicious": False, "score": 0.0, "reasons": []}

    async def _analyze_image_misuse(self, image_urls: List[str]) -> Dict:
        try:
            misuse_detected = False
            misuse_score = 0.0

            for url in image_urls:
                try:
                    mock_hash = "a1b2c3d4e5f6g7h8"
                    if mock_hash in self.official_image_hashes:
                        misuse_detected = True
                        misuse_score = 0.9
                        break
                except Exception as img_error:
                    self.logger.error(f"Error processing image {url}: {img_error}")
                    continue

            return {"is_misuse": misuse_detected, "score": misuse_score}

        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            return {"is_misuse": False, "score": 0.0}

    def _calculate_overall_score(self, scores: Dict) -> float:
        try:
            weights = {
                "toxicity": 0.3,
                "sentiment": 0.1,
                "fake_account": 0.2,
                "image_misuse": 0.15,
                "llm_confidence": 0.25
            }

            weighted_score = 0.0
            total_weight = 0.0

            for score_type, score_value in scores.items():
                if score_type in weights:
                    weighted_score += score_value * weights[score_type]
                    total_weight += weights[score_type]

            return weighted_score / total_weight if total_weight > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Error calculating overall score: {e}")
            return 0.0

    def _mock_toxic_classifier(self, content: str):
        threat_keywords = ["kill", "murder", "die", "hurt", "harm", "attack", "destroy"]
        is_toxic = any(keyword in content.lower() for keyword in threat_keywords)
        return [{"label": "TOXIC" if is_toxic else "NON_TOXIC",
                 "score": 0.8 if is_toxic else 0.2}]

    def _mock_sentiment_analyzer(self, content: str):
        negative_keywords = ["hate", "awful", "terrible", "disgusting", "worst"]
        is_negative = any(keyword in content.lower() for keyword in negative_keywords)
        return [{"label": "NEGATIVE" if is_negative else "POSITIVE",
                 "score": 0.7 if is_negative else 0.3}]
