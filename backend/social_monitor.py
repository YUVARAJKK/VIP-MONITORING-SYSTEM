import asyncio
import logging
import os
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

class SocialMediaMonitor:
    def __init__(self, threat_engine, database: AsyncIOMotorDatabase):
        self.threat_engine = threat_engine
        self.db = database
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        
        # Get monitoring configuration from environment
        self.vip_target = os.environ.get('VIP_TARGET_NAME', 'Celebrity VIP')
        self.vip_username = os.environ.get('VIP_TARGET_USERNAME', '@celebrityvip')
        self.keywords = os.environ.get('MONITORING_KEYWORDS', 'Celebrity VIP,@celebrityvip').split(',')
        
        # Mock data for demonstration
        self.mock_posts = self._generate_mock_posts()
        
    def _generate_mock_posts(self) -> List[Dict]:
        """Generate realistic mock social media posts for demonstration"""
        
        # Mix of normal, concerning, and threatening posts
        mock_posts = [
            # Benign posts
            {
                "platform": "Twitter",
                "author": "fan_user_1",
                "content": f"Love {self.vip_target}! Can't wait for the next movie!",
                "url": "https://twitter.com/fan_user_1/status/123456789",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "platform": "Instagram",
                "author": "movie_lover_42",
                "content": f"Just watched {self.vip_target}'s latest film. Amazing performance! 🎬",
                "url": "https://instagram.com/p/abc123def/",
                "images": ["https://example.com/image1.jpg"],
                "timestamp": datetime.now(timezone.utc)
            },
            
            # Negative sentiment posts
            {
                "platform": "Twitter",
                "author": "critic_user",
                "content": f"I really hate {self.vip_target}'s new movie. Worst acting ever!",
                "url": "https://twitter.com/critic_user/status/234567890",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "platform": "Facebook",
                "author": "disappointed_fan",
                "content": f"{self.vip_target} is so overrated. Terrible performance in everything.",
                "url": "https://facebook.com/posts/567890123",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            
            # Suspicious/bot accounts
            {
                "platform": "Twitter",
                "author": "bot_user_123",
                "content": f"{self.vip_target} should just quit acting. Nobody likes them anymore.",
                "url": "https://twitter.com/bot_user_123/status/345678901",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "platform": "Instagram",
                "author": "fake_account_456",
                "content": f"Why does {self.vip_target} even exist? So annoying!",
                "url": "https://instagram.com/p/def456ghi/",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            
            # Threatening/concerning posts
            {
                "platform": "Twitter",
                "author": "angry_user_789",
                "content": f"{self.vip_target} deserves to be hurt for what they did. Someone should teach them a lesson.",
                "url": "https://twitter.com/angry_user_789/status/456789012",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "platform": "Facebook",
                "author": "threatening_account",
                "content": f"I'm going to find {self.vip_target} and make them pay. They won't get away with this.",
                "url": "https://facebook.com/posts/789012345",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "platform": "Instagram",
                "author": "violent_user",
                "content": f"{self.vip_target} should die. The world would be better without them. I'll make sure of it.",
                "url": "https://instagram.com/p/ghi789jkl/",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            },
            
            # Misinformation/impersonation
            {
                "platform": "Twitter",
                "author": f"FAKE_{self.vip_username.replace('@', '').upper()}",
                "content": "I'm retiring from acting effective immediately. Thank you for all the support over the years.",
                "url": "https://twitter.com/fake_celebrity/status/567890123",
                "images": [],
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        return mock_posts
    
    async def start_monitoring(self):
        """Start the continuous monitoring process"""
        self.is_monitoring = True
        self.logger.info("Starting social media monitoring...")
        
        try:
            while self.is_monitoring:
                # Monitor each platform
                await self._monitor_twitter()
                await self._monitor_facebook()
                await self._monitor_instagram()
                
                # Wait before next monitoring cycle (30 seconds for demo)
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            self.logger.info("Monitoring cancelled")
            self.is_monitoring = False
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            self.is_monitoring = False
    
    async def stop_monitoring(self):
        """Stop the monitoring process"""
        self.is_monitoring = False
        self.logger.info("Stopping social media monitoring...")
    
    async def _monitor_twitter(self):
        """Monitor Twitter/X for threats"""
        try:
            # In a real implementation, this would use the Twitter API
            # For demonstration, we'll use mock data
            twitter_posts = [post for post in self.mock_posts if post["platform"] == "Twitter"]
            
            # Randomly select a post to "discover" (simulate real-time monitoring)
            if twitter_posts and random.random() < 0.3:  # 30% chance to find a post
                post = random.choice(twitter_posts)
                await self._process_post(post)
                
        except Exception as e:
            self.logger.error(f"Error monitoring Twitter: {e}")
    
    async def _monitor_facebook(self):
        """Monitor Facebook for threats"""
        try:
            # In a real implementation, this would use Facebook Graph API or scraping
            facebook_posts = [post for post in self.mock_posts if post["platform"] == "Facebook"]
            
            # Randomly select a post to "discover"
            if facebook_posts and random.random() < 0.2:  # 20% chance to find a post
                post = random.choice(facebook_posts)
                await self._process_post(post)
                
        except Exception as e:
            self.logger.error(f"Error monitoring Facebook: {e}")
    
    async def _monitor_instagram(self):
        """Monitor Instagram for threats"""
        try:
            # In a real implementation, this would use Instagram API or scraping
            instagram_posts = [post for post in self.mock_posts if post["platform"] == "Instagram"]
            
            # Randomly select a post to "discover"
            if instagram_posts and random.random() < 0.25:  # 25% chance to find a post
                post = random.choice(instagram_posts)
                await self._process_post(post)
                
        except Exception as e:
            self.logger.error(f"Error monitoring Instagram: {e}")
    
    async def _process_post(self, post: Dict):
        """Process a social media post for threats"""
        try:
            # Check if we've already processed this post
            existing_alert = await self.db.threat_alerts.find_one({
                "post_id": post.get("url", "").split("/")[-1],
                "platform": post["platform"]
            })
            
            if existing_alert:
                return  # Already processed
            
            # Analyze the post for threats
            analysis_result = await self.threat_engine.analyze_post(
                content=post["content"],
                author=post["author"],
                platform=post["platform"],
                post_url=post["url"],
                image_urls=post.get("images", [])
            )
            
            # Only create alert if threat is detected or score is significant
            if analysis_result["is_threat"] or analysis_result["overall_score"] > 0.3:
                await self._create_threat_alert(post, analysis_result)
                
        except Exception as e:
            self.logger.error(f"Error processing post: {e}")
    
    async def _create_threat_alert(self, post: Dict, analysis: Dict):
        """Create and store a threat alert"""
        try:
            # Generate unique post ID from URL
            post_id = post.get("url", "").split("/")[-1] or str(uuid.uuid4())[:8]
            
            alert_data = {
                "id": str(uuid.uuid4()),
                "post_id": post_id,
                "author": post["author"],
                "content": post["content"],
                "url": post["url"],
                "platform": post["platform"],
                "reason": ", ".join(analysis["reasons"]) if analysis["reasons"] else "General Concern",
                "score": analysis["overall_score"],
                "timestamp": datetime.now(timezone.utc),
                "ai_analysis": analysis["ai_analysis"],
                "threat_level": analysis["threat_level"]
            }
            
            # Store in database
            await self.db.threat_alerts.insert_one(alert_data)
            
            self.logger.info(f"Created threat alert for {post['platform']} post by {post['author']}")
            self.logger.info(f"Threat level: {analysis['threat_level']}, Score: {analysis['overall_score']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error creating threat alert: {e}")
    
    async def get_monitoring_stats(self) -> Dict:
        """Get monitoring statistics"""
        try:
            total_alerts = await self.db.threat_alerts.count_documents({})
            
            # Get alerts by platform
            platform_stats = {}
            for platform in ["Twitter", "Facebook", "Instagram"]:
                count = await self.db.threat_alerts.count_documents({"platform": platform})
                platform_stats[platform] = count
            
            # Get alerts by threat level
            threat_level_stats = {}
            for level in ["low", "medium", "high", "critical"]:
                count = await self.db.threat_alerts.count_documents({"threat_level": level})
                threat_level_stats[level] = count
            
            return {
                "total_alerts": total_alerts,
                "platform_stats": platform_stats,
                "threat_level_stats": threat_level_stats,
                "is_monitoring": self.is_monitoring
            }
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring stats: {e}")
            return {}