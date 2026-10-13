# data_extraction_service.py
import requests
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional

class PlatformDataExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def extract_leetcode_data(self, username: str) -> Dict:
        """Extract comprehensive LeetCode data"""
        try:
            # Main profile data
            profile_data = self._fetch_leetcode_profile(username)
            if not profile_data.get('success'):
                return profile_data
            
            # Recent submissions
            recent_submissions = self._fetch_leetcode_submissions(username)
            
            # Contest data
            contest_data = self._fetch_leetcode_contests(username)
            
            # Combine all data
            enhanced_data = {
                **profile_data,
                'recent_submissions': recent_submissions,
                'contest_data': contest_data,
                'weekly_solved': len([s for s in recent_submissions if self._is_recent_week(s.get('timestamp'))]),
                'monthly_solved': len([s for s in recent_submissions if self._is_recent_month(s.get('timestamp'))]),
                'last_active': recent_submissions[0].get('timestamp') if recent_submissions else None,
                'submission_languages': list(set([s.get('lang') for s in recent_submissions if s.get('lang')])),
                'problem_categories': self._analyze_problem_categories(recent_submissions)
            }
            
            return enhanced_data
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fetch_leetcode_profile(self, username: str) -> Dict:
        """Fetch basic LeetCode profile data"""
        url = "https://leetcode.com/graphql"
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                submitStats: submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
                profile {
                    ranking
                    userAvatar
                    realName
                    reputation
                }
            }
        }
        """
        
        response = self.session.post(url, json={
            'query': query,
            'variables': {'username': username}
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('matchedUser'):
                user_data = data['data']['matchedUser']
                
                stats = {'easy': 0, 'medium': 0, 'hard': 0, 'total': 0}
                if user_data.get('submitStats', {}).get('acSubmissionNum'):
                    for stat in user_data['submitStats']['acSubmissionNum']:
                        difficulty = stat['difficulty'].lower()
                        if difficulty in stats:
                            stats[difficulty] = stat['count']
                            stats['total'] += stat['count']
                
                return {
                    'success': True,
                    'username': user_data['username'],
                    'solved_problems': stats,
                    'ranking': user_data.get('profile', {}).get('ranking', 0),
                    'reputation': user_data.get('profile', {}).get('reputation', 0)
                }
        
        return {'success': False, 'error': 'User not found or API error'}
    
    def _fetch_leetcode_submissions(self, username: str, limit: int = 50) -> List[Dict]:
        """Fetch recent LeetCode submissions"""
        try:
            url = "https://leetcode.com/graphql"
            query = """
            query getRecentSubmissions($username: String!, $limit: Int!) {
                recentSubmissionList(username: $username, limit: $limit) {
                    title
                    titleSlug
                    timestamp
                    statusDisplay
                    lang
                }
            }
            """
            
            response = self.session.post(url, json={
                'query': query,
                'variables': {'username': username, 'limit': limit}
            })
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get('data', {}).get('recentSubmissionList', [])
                
                # Filter only accepted submissions
                accepted_submissions = []
                for submission in submissions:
                    if submission.get('statusDisplay') == 'Accepted':
                        accepted_submissions.append({
                            'title': submission.get('title'),
                            'slug': submission.get('titleSlug'),
                            'timestamp': submission.get('timestamp'),
                            'language': submission.get('lang'),
                            'date': datetime.fromtimestamp(int(submission.get('timestamp', 0))).isoformat()
                        })
                
                return accepted_submissions
            
            return []
            
        except Exception as e:
            print(f"Error fetching LeetCode submissions: {e}")
            return []
    
    def _fetch_leetcode_contests(self, username: str) -> Dict:
        """Fetch LeetCode contest data"""
        try:
            url = "https://leetcode.com/graphql"
            query = """
            query getUserContestRanking($username: String!) {
                userContestRanking(username: $username) {
                    attendedContestsCount
                    rating
                    globalRanking
                    totalParticipants
                    topPercentage
                }
            }
            """
            
            response = self.session.post(url, json={
                'query': query,
                'variables': {'username': username}
            })
            
            if response.status_code == 200:
                data = response.json()
                contest_data = data.get('data', {}).get('userContestRanking')
                
                if contest_data:
                    return {
                        'contests_attended': contest_data.get('attendedContestsCount', 0),
                        'rating': contest_data.get('rating', 0),
                        'global_ranking': contest_data.get('globalRanking', 0),
                        'top_percentage': contest_data.get('topPercentage', 0)
                    }
            
            return {'contests_attended': 0, 'rating': 0, 'global_ranking': 0, 'top_percentage': 0}
            
        except Exception as e:
            print(f"Error fetching LeetCode contests: {e}")
            return {'contests_attended': 0, 'rating': 0, 'global_ranking': 0, 'top_percentage': 0}
    
    def extract_hackerrank_data(self, username: str) -> Dict:
        """Extract comprehensive HackerRank data"""
        try:
            # Main profile data
            profile_data = self._fetch_hackerrank_profile(username)
            if not profile_data.get('success'):
                return profile_data
            
            # Badges and certificates
            badges_data = self._fetch_hackerrank_badges(username)
            
            # Skills data
            skills_data = self._fetch_hackerrank_skills(username)
            
            # Combine all data
            enhanced_data = {
                **profile_data,
                'badges': badges_data,
                'skills': skills_data,
                'badge_count': len(badges_data),
                'skill_count': len(skills_data),
                'certificates': len([b for b in badges_data if 'certificate' in b.get('name', '').lower()]),
                'total_score': sum([skill.get('score', 0) for skill in skills_data])
            }
            
            return enhanced_data
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fetch_hackerrank_profile(self, username: str) -> Dict:
        """Fetch basic HackerRank profile data"""
        try:
            url = f"https://www.hackerrank.com/rest/hackers/{username}/scores"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                scores = {
                    'algorithms': 0,
                    'data_structures': 0,
                    'mathematics': 0,
                    'sql': 0,
                    'total_score': 0
                }
                
                if data.get('models'):
                    for model in data['models']:
                        domain = model.get('name', '').lower()
                        score = model.get('score', 0)
                        
                        if 'algorithm' in domain:
                            scores['algorithms'] = score
                        elif 'data' in domain and 'structure' in domain:
                            scores['data_structures'] = score
                        elif 'mathematics' in domain:
                            scores['mathematics'] = score
                        elif 'sql' in domain:
                            scores['sql'] = score
                        
                        scores['total_score'] += score
                
                return {
                    'success': True,
                    'username': username,
                    'scores': scores
                }
            
            return {'success': False, 'error': 'User not found or API error'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fetch_hackerrank_badges(self, username: str) -> List[Dict]:
        """Fetch HackerRank badges"""
        try:
            url = f"https://www.hackerrank.com/rest/hackers/{username}/badges"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                badges = []
                
                for badge in data.get('models', []):
                    badges.append({
                        'name': badge.get('badge_name'),
                        'level': badge.get('level'),
                        'earned_date': badge.get('created_at')
                    })
                
                return badges
            
            return []
            
        except Exception as e:
            print(f"Error fetching HackerRank badges: {e}")
            return []
    
    def _fetch_hackerrank_skills(self, username: str) -> List[Dict]:
        """Fetch HackerRank skills data"""
        try:
            # This would require additional API endpoints or web scraping
            # For now, return basic structure
            return []
            
        except Exception as e:
            print(f"Error fetching HackerRank skills: {e}")
            return []
    
    def _is_recent_week(self, timestamp) -> bool:
        """Check if timestamp is within last week"""
        if not timestamp:
            return False
        try:
            date = datetime.fromtimestamp(int(timestamp))
            return date >= datetime.now() - timedelta(days=7)
        except:
            return False
    
    def _is_recent_month(self, timestamp) -> bool:
        """Check if timestamp is within last month"""
        if not timestamp:
            return False
        try:
            date = datetime.fromtimestamp(int(timestamp))
            return date >= datetime.now() - timedelta(days=30)
        except:
            return False
    
    def _analyze_problem_categories(self, submissions: List[Dict]) -> Dict:
        """Analyze problem categories from submissions"""
        # This would require additional data about problem categories
        # For now, return basic structure
        return {
            'array': 0,
            'string': 0,
            'dynamic_programming': 0,
            'tree': 0,
            'graph': 0,
            'other': len(submissions)
        }
    
    def extract_combined_data(self, leetcode_username: str = None, hackerrank_username: str = None) -> Dict:
        """Extract and combine data from both platforms"""
        result = {
            'leetcode': None,
            'hackerrank': None,
            'combined_metrics': {},
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Extract LeetCode data
        if leetcode_username:
            result['leetcode'] = self.extract_leetcode_data(leetcode_username)
        
        # Extract HackerRank data
        if hackerrank_username:
            result['hackerrank'] = self.extract_hackerrank_data(hackerrank_username)
        
        # Calculate combined metrics
        result['combined_metrics'] = self._calculate_combined_metrics(
            result['leetcode'], result['hackerrank']
        )
        
        return result
    
    def _calculate_combined_metrics(self, leetcode_data: Dict, hackerrank_data: Dict) -> Dict:
        """Calculate combined metrics from both platforms"""
        metrics = {
            'total_problems_solved': 0,
            'total_score': 0,
            'platform_count': 0,
            'weekly_activity': 0,
            'skill_diversity': 0
        }
        
        if leetcode_data and leetcode_data.get('success'):
            metrics['total_problems_solved'] += leetcode_data.get('solved_problems', {}).get('total', 0)
            metrics['weekly_activity'] += leetcode_data.get('weekly_solved', 0)
            metrics['platform_count'] += 1
        
        if hackerrank_data and hackerrank_data.get('success'):
            metrics['total_score'] += hackerrank_data.get('total_score', 0)
            metrics['skill_diversity'] += hackerrank_data.get('skill_count', 0)
            metrics['platform_count'] += 1
        
        return metrics

# Global instance
data_extractor = PlatformDataExtractor()