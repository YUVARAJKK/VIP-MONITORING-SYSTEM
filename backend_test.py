#!/usr/bin/env python3
"""
Comprehensive Backend Testing for VIP Threat Monitoring System
Tests all API endpoints, AI models, database operations, and monitoring functionality
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VIPThreatMonitoringTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self._get_backend_url()
        self.session = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": {}
        }
        
    def _get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        return f"{url}/api"
            return "https://threatwatch-2.preview.emergentagent.com/api"
        except Exception as e:
            logger.error(f"Could not read backend URL from .env: {e}")
            return "https://threatwatch-2.preview.emergentagent.com/api"
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        logger.info(f"Testing backend at: {self.base_url}")
    
    async def teardown(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {error}")
            logger.error(f"❌ {test_name}: FAILED - {error}")
        
        self.test_results["details"][test_name] = {
            "success": success,
            "details": details,
            "error": error
        }
    
    async def test_health_check(self):
        """Test GET /api/ - basic health check"""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "VIP Threat Monitoring" in data["message"]:
                        self.log_test_result("Health Check", True, f"Response: {data['message']}")
                    else:
                        self.log_test_result("Health Check", False, error=f"Unexpected response: {data}")
                else:
                    self.log_test_result("Health Check", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Health Check", False, error=str(e))
    
    async def test_get_alerts(self):
        """Test GET /api/alerts - retrieve all threat alerts"""
        try:
            async with self.session.get(f"{self.base_url}/alerts") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test_result("Get All Alerts", True, f"Retrieved {len(data)} alerts")
                        return data
                    else:
                        self.log_test_result("Get All Alerts", False, error=f"Expected list, got: {type(data)}")
                else:
                    self.log_test_result("Get All Alerts", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Get All Alerts", False, error=str(e))
        return []
    
    async def test_get_recent_alerts(self):
        """Test GET /api/alerts/recent - recent alerts (24h)"""
        try:
            async with self.session.get(f"{self.base_url}/alerts/recent") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test_result("Get Recent Alerts", True, f"Retrieved {len(data)} recent alerts")
                        return data
                    else:
                        self.log_test_result("Get Recent Alerts", False, error=f"Expected list, got: {type(data)}")
                else:
                    self.log_test_result("Get Recent Alerts", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Get Recent Alerts", False, error=str(e))
        return []
    
    async def test_monitoring_status(self):
        """Test GET /api/status - monitoring status"""
        try:
            async with self.session.get(f"{self.base_url}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["is_running", "platforms_monitored", "alerts_count", "last_check"]
                    if all(field in data for field in required_fields):
                        platforms = data["platforms_monitored"]
                        expected_platforms = ["Twitter", "Facebook", "Instagram"]
                        if all(platform in platforms for platform in expected_platforms):
                            self.log_test_result("Monitoring Status", True, 
                                               f"Status: {data['is_running']}, Alerts: {data['alerts_count']}")
                            return data
                        else:
                            self.log_test_result("Monitoring Status", False, 
                                               error=f"Missing platforms. Got: {platforms}")
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_test_result("Monitoring Status", False, 
                                           error=f"Missing fields: {missing}")
                else:
                    self.log_test_result("Monitoring Status", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Monitoring Status", False, error=str(e))
        return None
    
    async def test_start_monitoring(self):
        """Test POST /api/monitoring/start - start monitoring"""
        try:
            async with self.session.post(f"{self.base_url}/monitoring/start") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and ("started" in data["message"].lower() or "running" in data["message"].lower()):
                        self.log_test_result("Start Monitoring", True, f"Response: {data['message']}")
                        return True
                    else:
                        self.log_test_result("Start Monitoring", False, error=f"Unexpected response: {data}")
                else:
                    self.log_test_result("Start Monitoring", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Start Monitoring", False, error=str(e))
        return False
    
    async def test_stop_monitoring(self):
        """Test POST /api/monitoring/stop - stop monitoring"""
        try:
            async with self.session.post(f"{self.base_url}/monitoring/stop") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and ("stopped" in data["message"].lower() or "not running" in data["message"].lower()):
                        self.log_test_result("Stop Monitoring", True, f"Response: {data['message']}")
                        return True
                    else:
                        self.log_test_result("Stop Monitoring", False, error=f"Unexpected response: {data}")
                else:
                    self.log_test_result("Stop Monitoring", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Stop Monitoring", False, error=str(e))
        return False
    
    async def test_generate_mock_alert(self):
        """Test GET /api/test/generate-mock-alert - generate test alert"""
        try:
            async with self.session.get(f"{self.base_url}/test/generate-mock-alert") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "alert" in data:
                        alert = data["alert"]
                        required_fields = ["id", "post_id", "author", "content", "platform", "threat_level"]
                        if all(field in alert for field in required_fields):
                            self.log_test_result("Generate Mock Alert", True, 
                                               f"Created alert: {alert['threat_level']} level from {alert['platform']}")
                            return alert
                        else:
                            missing = [f for f in required_fields if f not in alert]
                            self.log_test_result("Generate Mock Alert", False, 
                                               error=f"Alert missing fields: {missing}")
                    else:
                        self.log_test_result("Generate Mock Alert", False, 
                                           error=f"Missing message or alert in response: {data}")
                else:
                    self.log_test_result("Generate Mock Alert", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Generate Mock Alert", False, error=str(e))
        return None
    
    async def test_clear_alerts(self):
        """Test DELETE /api/alerts - clear all alerts"""
        try:
            async with self.session.delete(f"{self.base_url}/alerts") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "cleared" in data["message"].lower():
                        self.log_test_result("Clear Alerts", True, f"Response: {data['message']}")
                        return True
                    else:
                        self.log_test_result("Clear Alerts", False, error=f"Unexpected response: {data}")
                else:
                    self.log_test_result("Clear Alerts", False, error=f"HTTP {response.status}")
        except Exception as e:
            self.log_test_result("Clear Alerts", False, error=str(e))
        return False
    
    async def test_ai_threat_detection_workflow(self):
        """Test complete AI threat detection workflow"""
        try:
            # 1. Clear existing alerts
            await self.test_clear_alerts()
            await asyncio.sleep(1)
            
            # 2. Generate a mock alert (this tests AI analysis)
            alert = await self.test_generate_mock_alert()
            if not alert:
                self.log_test_result("AI Threat Detection Workflow", False, 
                                   error="Failed to generate mock alert")
                return
            
            await asyncio.sleep(1)
            
            # 3. Verify alert was stored in database
            alerts = await self.test_get_alerts()
            if len(alerts) > 0:
                stored_alert = alerts[0]
                # Check if AI analysis fields are present
                ai_fields = ["ai_analysis", "threat_level", "score"]
                if all(field in stored_alert for field in ai_fields):
                    self.log_test_result("AI Threat Detection Workflow", True, 
                                       f"AI analysis complete: {stored_alert['threat_level']} threat, score: {stored_alert['score']}")
                else:
                    missing = [f for f in ai_fields if f not in stored_alert]
                    self.log_test_result("AI Threat Detection Workflow", False, 
                                       error=f"Stored alert missing AI fields: {missing}")
            else:
                self.log_test_result("AI Threat Detection Workflow", False, 
                                   error="Alert not found in database after generation")
                
        except Exception as e:
            self.log_test_result("AI Threat Detection Workflow", False, error=str(e))
    
    async def test_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        try:
            # 1. Check initial status
            initial_status = await self.test_monitoring_status()
            if not initial_status:
                self.log_test_result("Monitoring Workflow", False, error="Failed to get initial status")
                return
            
            # 2. Start monitoring
            start_success = await self.test_start_monitoring()
            if not start_success:
                self.log_test_result("Monitoring Workflow", False, error="Failed to start monitoring")
                return
            
            await asyncio.sleep(2)
            
            # 3. Check status after starting
            running_status = await self.test_monitoring_status()
            if running_status and running_status.get("is_running"):
                self.log_test_result("Monitoring Workflow - Status Check", True, 
                                   "Monitoring confirmed running")
            else:
                self.log_test_result("Monitoring Workflow - Status Check", False, 
                                   error="Monitoring not showing as running")
            
            # 4. Let it run for a bit to potentially generate alerts
            logger.info("Letting monitoring run for 35 seconds to generate alerts...")
            await asyncio.sleep(35)
            
            # 5. Check if any alerts were generated
            alerts_after_monitoring = await self.test_get_alerts()
            
            # 6. Stop monitoring
            stop_success = await self.test_stop_monitoring()
            if not stop_success:
                self.log_test_result("Monitoring Workflow", False, error="Failed to stop monitoring")
                return
            
            await asyncio.sleep(1)
            
            # 7. Verify monitoring stopped
            stopped_status = await self.test_monitoring_status()
            if stopped_status and not stopped_status.get("is_running"):
                self.log_test_result("Monitoring Workflow", True, 
                                   f"Complete workflow successful. Generated {len(alerts_after_monitoring)} alerts during monitoring")
            else:
                self.log_test_result("Monitoring Workflow", False, 
                                   error="Monitoring not showing as stopped")
                
        except Exception as e:
            self.log_test_result("Monitoring Workflow", False, error=str(e))
    
    async def test_database_operations(self):
        """Test database operations and data persistence"""
        try:
            # 1. Clear alerts
            await self.test_clear_alerts()
            await asyncio.sleep(1)
            
            # 2. Verify database is empty
            empty_alerts = await self.test_get_alerts()
            if len(empty_alerts) != 0:
                self.log_test_result("Database Operations", False, 
                                   error=f"Database not empty after clear: {len(empty_alerts)} alerts")
                return
            
            # 3. Generate multiple alerts
            alerts_created = []
            for i in range(3):
                alert = await self.test_generate_mock_alert()
                if alert:
                    alerts_created.append(alert)
                await asyncio.sleep(0.5)
            
            if len(alerts_created) != 3:
                self.log_test_result("Database Operations", False, 
                                   error=f"Failed to create 3 alerts, only created {len(alerts_created)}")
                return
            
            # 4. Verify all alerts are stored
            stored_alerts = await self.test_get_alerts()
            if len(stored_alerts) >= 3:
                # 5. Test recent alerts functionality
                recent_alerts = await self.test_get_recent_alerts()
                if len(recent_alerts) >= 3:
                    self.log_test_result("Database Operations", True, 
                                       f"Successfully stored and retrieved {len(stored_alerts)} alerts")
                else:
                    self.log_test_result("Database Operations", False, 
                                       error=f"Recent alerts query failed: {len(recent_alerts)} vs {len(stored_alerts)}")
            else:
                self.log_test_result("Database Operations", False, 
                                   error=f"Not all alerts stored: {len(stored_alerts)} vs 3 expected")
                
        except Exception as e:
            self.log_test_result("Database Operations", False, error=str(e))
    
    async def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test invalid endpoint
            async with self.session.get(f"{self.base_url}/invalid-endpoint") as response:
                if response.status == 404:
                    self.log_test_result("Error Handling - Invalid Endpoint", True, 
                                       "Correctly returned 404 for invalid endpoint")
                else:
                    self.log_test_result("Error Handling - Invalid Endpoint", False, 
                                       error=f"Expected 404, got {response.status}")
        except Exception as e:
            self.log_test_result("Error Handling", False, error=str(e))
    
    async def run_all_tests(self):
        """Run all backend tests"""
        logger.info("🚀 Starting VIP Threat Monitoring System Backend Tests")
        logger.info("=" * 60)
        
        await self.setup()
        
        try:
            # Basic API Tests
            logger.info("📡 Testing Basic API Endpoints...")
            await self.test_health_check()
            await self.test_monitoring_status()
            
            # Alert Management Tests
            logger.info("🚨 Testing Alert Management...")
            await self.test_get_alerts()
            await self.test_get_recent_alerts()
            await self.test_generate_mock_alert()
            await self.test_clear_alerts()
            
            # Monitoring Control Tests
            logger.info("👁️ Testing Monitoring Controls...")
            await self.test_start_monitoring()
            await self.test_stop_monitoring()
            
            # Advanced Workflow Tests
            logger.info("🤖 Testing AI Threat Detection Workflow...")
            await self.test_ai_threat_detection_workflow()
            
            logger.info("💾 Testing Database Operations...")
            await self.test_database_operations()
            
            logger.info("🔄 Testing Complete Monitoring Workflow...")
            await self.test_monitoring_workflow()
            
            # Error Handling Tests
            logger.info("⚠️ Testing Error Handling...")
            await self.test_error_handling()
            
        finally:
            await self.teardown()
        
        # Print final results
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        if failed > 0:
            logger.info("\n🔍 FAILED TESTS:")
            for error in self.test_results["errors"]:
                logger.error(f"  • {error}")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results["details"].items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"  {status}: {test_name}")
            if result["details"]:
                logger.info(f"    Details: {result['details']}")
            if result["error"]:
                logger.info(f"    Error: {result['error']}")
        
        return self.test_results

async def main():
    """Main test execution"""
    tester = VIPThreatMonitoringTester()
    await tester.run_all_tests()
    
    # Return exit code based on test results
    if tester.test_results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())