import asyncio
import aiohttp
import random
from datetime import datetime
import os, re
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8080" # "https://test.mascyp.org"
EVENT_ID = 1  # Change to your test event ID

# Sample questions
SAMPLE_QUESTIONS = [
    "What is the main topic of this session?",
    "Can you elaborate on that point?",
    "How does this compare to previous research?",
    "What are the practical applications?",
    "Could you recommend some resources?",
    "What's your opinion on this approach?",
    "How can we implement this in real-world scenarios?",
    "Are there any limitations to this method?",
]

class SimulatedUser:
    def __init__(self, user_id: int, base_url: str, event_id: int):
        self.user_id = user_id
        self.base_url = base_url
        self.event_id = event_id
        self.session = None
        self.cookies = None
        self.output_dir = "tests/output"
        self.submitted_question_ids = []  # Store UUIDs of submitted questions
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def create_session(self):
        """Create an HTTP session with cookies (simulates a user session)"""
        # Create session with cookie jar that handles cookies automatically
        self.session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True)  # Allow cookies for any domain
        )
        print(f"✓ User {self.user_id}: Session created")
    
    async def login_as_moderator(self, username: str, password: str):
        """Login as moderator/admin"""
        data = aiohttp.FormData()
        data.add_field('username', username)
        data.add_field('password', password)
        
        # POST to login endpoint
        async with self.session.post(
            f"{self.base_url}/admin/login",
            data=data,
            allow_redirects=False  # Don't follow redirects, check the response
        ) as resp:
            print(f"🔐 Login response status: {resp.status}, URL: {resp.url}")
            
            # Check all cookies (including session cookies)
            cookies_dict = {}
            for cookie in self.session.cookie_jar:
                cookies_dict[cookie.key] = cookie.value
            
            print(f"🍪 Cookies after login: {list(cookies_dict.keys())}")
            
            # Check for HX-Refresh header (FastHTML's way of indicating success)
            if 'HX-Refresh' in resp.headers:
                print(f"✓ User {self.user_id}: Logged in as moderator '{username}' (HX-Refresh header present)")
                # Give the session a moment to propagate
                await asyncio.sleep(0.5)
                return True
            
            # If no HX-Refresh, login failed - check the response
            response_text = await resp.text()
            if 'Invalid username or password' in response_text:
                print(f"✗ User {self.user_id}: Invalid credentials")
                return False
            
            # Check if we got any session-related cookies
            if len(cookies_dict) > 0:
                print(f"✓ User {self.user_id}: Logged in as moderator '{username}' (session cookie present)")
                await asyncio.sleep(0.5)
                return True
                
            print(f"✗ User {self.user_id}: Moderator login failed")
            print(f"   Response preview: {response_text[:200]}")
            return False
        
    async def login_as_moderator_test_mode(self, username: str, password: str):
        """Use test endpoint to bypass login (requires ENVIRONMENT=test)"""
        async with self.session.post(
            f"{self.base_url}/admin/test_login",
            data={'username': username, 'password': password}
        ) as resp:
            if resp.status == 200:
                print(f"✅ User {self.user_id}: Logged in as moderator via test endpoint")
                await asyncio.sleep(0.5)
                return True
            else:
                print(f"❌ Test login endpoint not available (status {resp.status})")
                return False
            

    async def verify_moderator_access(self):
        """Verify that moderator session is working by trying to access moderator page"""
        async with self.session.get(
            f"{self.base_url}/admin_dashboard",
            allow_redirects=False
        ) as resp:
            print(f"🔍 Verification: Dashboard access returned status {resp.status}")
            
            if resp.status == 200:
                html = await resp.text()
                if 'Admin Dashboard' in html:
                    print(f"✅ Moderator access verified - can access dashboard")
                    return True
                else:
                    print(f"⚠️  Got 200 but unexpected content")
                    return False
            elif resp.status == 303:
                print(f"❌ Moderator access denied - redirected to login")
                return False
            else:
                print(f"❌ Unexpected status: {resp.status}")
                return False

    async def get_question_ids(self):
        """Fetch all question UUIDs from the moderator page"""
        # Moderators should fetch from moderator page to see ALL questions
        endpoint = f"{self.base_url}/qa/moderator/event/{self.event_id}"
        
        async with self.session.get(endpoint) as resp:
            if resp.status == 200:
                html = await resp.text()
                
                # Check if we're actually on the moderator page
                if 'login' in html.lower() and 'admin' in html.lower():
                    print(f"⚠️  User {self.user_id}: Not authenticated - got login page")
                    return []
                
                # Extract UUIDs from HTML (pattern: UUID format)
                uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                uuids = re.findall(uuid_pattern, html)
                unique_uuids = list(set(uuids))  # Remove duplicates
                print(f"✓ User {self.user_id}: Found {len(unique_uuids)} question UUIDs")
                return unique_uuids
            else:
                print(f"✗ User {self.user_id}: Failed to fetch questions (status {resp.status})")
                return []

    async def submit_question(self, question_text: str):
        """Submit a question and try to capture its UUID"""
        # Get a random nickname for variety
        nickname = f"TestUser{self.user_id}"
        
        data = aiohttp.FormData()
        data.add_field('question_text', question_text)
        data.add_field('nickname', nickname)
        
        async with self.session.post(
            f"{self.base_url}/qa/event/{self.event_id}/submit",
            data=data
        ) as resp:
            if resp.status == 200:
                response_text = await resp.text()
                # Try to extract UUID from response
                uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                uuids = re.findall(uuid_pattern, response_text)
                if uuids:
                    self.submitted_question_ids.append(uuids[0])
                print(f"✓ User {self.user_id} ({nickname}): Submitted question: '{question_text[:50]}...'")
            else:
                print(f"✗ User {self.user_id}: Failed to submit question (status {resp.status})")

    async def like_question(self, question_uuid: str):
        """Like a question using UUID"""
        async with self.session.post(
            f"{self.base_url}/qa/question/{question_uuid}/like"
        ) as resp:
            if resp.status == 200:
                print(f"✓ User {self.user_id}: Liked question {question_uuid[:8]}...")
            else:
                print(f"✗ User {self.user_id}: Failed to like question {question_uuid[:8]}...")

    async def listen_to_sse(self, duration: int = 30):
        """Listen to SSE stream"""
        print(f"👂 User {self.user_id}: Listening to SSE stream...")
        try:
            async with self.session.get(
                f"{self.base_url}/qa/{self.event_id}/stream",
                timeout=aiohttp.ClientTimeout(total=duration)
            ) as resp:
                async for line in resp.content:
                    if line:
                        decoded = line.decode('utf-8').strip()
                        if decoded.startswith('data:'):
                            print(f"📨 User {self.user_id}: Received SSE: {decoded[:100]}...")
        except asyncio.TimeoutError:
            print(f"⏱️  User {self.user_id}: SSE stream ended (timeout)")
        except Exception as e:
            print(f"✗ User {self.user_id}: SSE error: {e}")
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

    async def show_question(self, question_uuid: str, save_response: bool = False):
        """Show (approve) a question as moderator using UUID"""
        async with self.session.post(
            f"{self.base_url}/qa/moderator/question/{question_uuid}/toggle-visibility"
        ) as resp:
            if resp.status == 200:
                print(f"✓ Moderator {self.user_id}: Toggled visibility for question {question_uuid[:8]}...")
                if save_response:
                    await self._save_html_response(resp, f"toggle_visibility_{question_uuid[:8]}")
            else:
                print(f"✗ Moderator {self.user_id}: Failed to toggle visibility for question {question_uuid[:8]}... (status {resp.status})")

    async def hide_question(self, question_uuid: str, save_response: bool = False):
        """Hide a question as moderator using UUID"""
        # Same endpoint as show - it's a toggle
        async with self.session.post(
            f"{self.base_url}/qa/moderator/question/{question_uuid}/toggle-visibility"
        ) as resp:
            if resp.status == 200:
                print(f"✓ Moderator {self.user_id}: Toggled visibility for question {question_uuid[:8]}...")
                if save_response:
                    await self._save_html_response(resp, f"toggle_visibility_{question_uuid[:8]}")
            else:
                print(f"✗ Moderator {self.user_id}: Failed to toggle visibility for question {question_uuid[:8]}... (status {resp.status})")

    async def mark_answered(self, question_uuid: str, save_response: bool = False):
        """Mark a question as answered"""
        async with self.session.post(
            f"{self.base_url}/qa/moderator/question/{question_uuid}/toggle-answered"
        ) as resp:
            if resp.status == 200:
                print(f"✓ Moderator {self.user_id}: Toggled answered status for question {question_uuid[:8]}...")
                if save_response:
                    await self._save_html_response(resp, f"toggle_answered_{question_uuid[:8]}")
            else:
                print(f"✗ Moderator {self.user_id}: Failed to toggle answered status for question {question_uuid[:8]}...")

    async def delete_question(self, question_uuid: str):
        """Delete a question as moderator"""
        async with self.session.delete(
            f"{self.base_url}/qa/moderator/question/{question_uuid}"
        ) as resp:
            if resp.status == 200:
                print(f"✓ Moderator {self.user_id}: Deleted question {question_uuid[:8]}...")
            else:
                print(f"✗ Moderator {self.user_id}: Failed to delete question {question_uuid[:8]}...")

    async def activate_session(self, save_response: bool = False):
        """Activate the Q&A session"""
        async with self.session.post(
            f"{self.base_url}/qa/moderator/event/{self.event_id}/toggle-qa"
        ) as resp:
            if resp.status == 200:
                print(f"✓ Moderator {self.user_id}: Toggled Q&A for event {self.event_id}")
                if save_response:
                    await self._save_html_response(resp, f"toggle_qa_{self.event_id}")
            else:
                print(f"✗ Moderator {self.user_id}: Failed to toggle Q&A (status {resp.status})")

    async def _save_html_response(self, resp, filename_prefix: str):
        """Save HTML response to file"""
        content = await resp.text()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/{filename_prefix}_user{self.user_id}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 User {self.user_id}: Saved response to {filename}")
    
    async def get_qa_page(self, save_response: bool = False, moderator: bool = False):
        """Get the Q&A page HTML (guest view)"""
        async with self.session.get(
            f"{self.base_url}/qa{"/moderator" if moderator else ""}/event/{self.event_id}"
        ) as resp:
            if resp.status == 200:
                html = await resp.text()
                
                # Verify it's not a login page
                if 'login' in html.lower() and 'password' in html.lower() and len(html) < 5000:
                    print(f"⚠️  User {self.user_id}: Got login page instead of Q&A page")
                    if save_response:
                        await self._save_html_response(resp, f"qa_page_LOGIN_ERROR_{self.event_id}")
                    return None
                    
                print(f"✓ User {self.user_id}: Fetched Q&A page")
                if save_response:
                    await self._save_html_response(resp, f"qa_page_{self.event_id}")
                return html
            else:
                print(f"✗ User {self.user_id}: Failed to fetch Q&A page (status {resp.status})")
                return None

    async def get_moderator_page(self, save_response: bool = False):
        """Get the moderator Q&A page HTML"""
        async with self.session.get(
            f"{self.base_url}/qa/moderator/event/{self.event_id}"
        ) as resp:
            if resp.status == 200:
                html = await resp.text()
                
                # Check if we got redirected to login
                if 'login' in html.lower() and len(html) < 5000:
                    print(f"⚠️  Moderator {self.user_id}: Got login page instead of moderator page")
                    if save_response:
                        await self._save_html_response(resp, f"moderator_page_LOGIN_ERROR_{self.event_id}")
                    return None
                
                print(f"✓ Moderator {self.user_id}: Fetched moderator Q&A page")
                if save_response:
                    await self._save_html_response(resp, f"moderator_page_{self.event_id}")
                return html
            else:
                print(f"✗ Moderator {self.user_id}: Failed to fetch moderator page (status {resp.status})")
                return None

    async def verify_question_visible_on_page(self, question_uuid: str) -> bool:
        """Verify a question appears on the guest page"""
        html = await self.get_qa_page(save_response=False)
        if not html:
            return False
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for the question by data-question-id attribute
        question_card = soup.find('div', attrs={'data-question-id': question_uuid})
        
        if question_card:
            # Extract question text for confirmation
            question_text_elem = question_card.find(class_='question-text')
            question_text = question_text_elem.text.strip() if question_text_elem else "N/A"
            print(f"✅ User {self.user_id}: Question {question_uuid[:8]} IS VISIBLE - '{question_text[:50]}...'")
            return True
        else:
            print(f"❌ User {self.user_id}: Question {question_uuid[:8]} NOT VISIBLE on page")
            return False
    
    async def verify_question_hidden_on_page(self, question_uuid: str) -> bool:
        """Verify a question does NOT appear on the guest page"""
        html = await self.get_qa_page(save_response=False)
        if not html:
            return False
        
        soup = BeautifulSoup(html, 'html.parser')
        question_card = soup.find('div', attrs={'data-question-id': question_uuid})
        
        if not question_card:
            print(f"✅ User {self.user_id}: Question {question_uuid[:8]} IS HIDDEN (correct)")
            return True
        else:
            print(f"❌ User {self.user_id}: Question {question_uuid[:8]} STILL VISIBLE (incorrect)")
            return False
    
    async def count_visible_questions(self) -> int:
        """Count how many questions are visible on the guest page"""
        html = await self.get_qa_page(save_response=False)
        if not html:
            return 0
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all question cards
        questions = soup.find_all('div', attrs={'data-question-id': True})
        count = len(questions)
        print(f"📊 User {self.user_id}: Found {count} visible questions on page")
        return count
    
    async def get_all_visible_question_ids(self) -> list:
        """Get all visible question UUIDs from the guest page"""
        html = await self.get_qa_page(save_response=False)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        questions = soup.find_all('div', attrs={'data-question-id': True})
        
        question_ids = [q['data-question-id'] for q in questions]
        print(f"📋 User {self.user_id}: Visible question IDs: {[qid[:8] for qid in question_ids]}")
        return question_ids
    
    async def verify_question_answered_status(self, question_uuid: str) -> bool:
        """Check if a question is marked as answered on the page"""
        html = await self.get_qa_page(save_response=False)
        if not html:
            return False
        
        soup = BeautifulSoup(html, 'html.parser')
        question_card = soup.find('div', attrs={'data-question-id': question_uuid})
        
        if question_card:
            # Look for the answered badge with the specific class
            answered_badge = question_card.find('span', class_='question-answered-badge')
            
            # Alternative: look for the data-answered attribute
            answered_by_attr = question_card.find('span', attrs={'data-answered': 'true'})
            
            if answered_badge or answered_by_attr:
                print(f"✅ Question {question_uuid[:8]} IS marked as answered")
                return True
            else:
                print(f"ℹ️  Question {question_uuid[:8]} is NOT marked as answered")
                return False
        else:
            print(f"❌ Question {question_uuid[:8]} not found on page")
            return False

    async def get_question_list_only(self) -> str:
        """Get just the questions list HTML (lighter than full page)"""
        async with self.session.get(
            f"{self.base_url}/qa/event/{self.event_id}/questions"
        ) as resp:
            if resp.status == 200:
                html = await resp.text()
                print(f"✓ User {self.user_id}: Fetched questions list")
                return html
            else:
                print(f"✗ User {self.user_id}: Failed to fetch questions list (status {resp.status})")
                return None

    async def verify_question_visible_in_list(self, question_uuid: str) -> bool:
        """Verify a question appears in the questions list (more efficient)"""
        html = await self.get_question_list_only()
        if not html:
            return False
        
        soup = BeautifulSoup(html, 'html.parser')
        question_card = soup.find('div', attrs={'data-question-id': question_uuid})
        
        if question_card:
            question_text_elem = question_card.find(class_='question-text')
            question_text = question_text_elem.text.strip() if question_text_elem else "N/A"
            print(f"✅ User {self.user_id}: Question {question_uuid[:8]} IS VISIBLE - '{question_text[:50]}...'")
            return True
        else:
            print(f"❌ User {self.user_id}: Question {question_uuid[:8]} NOT VISIBLE in list")
            return False

    async def count_visible_questions_in_list(self) -> int:
        """Count questions in list (more efficient than full page)"""
        html = await self.get_question_list_only()
        if not html:
            return 0
        
        soup = BeautifulSoup(html, 'html.parser')
        questions = soup.find_all('div', attrs={'data-question-id': True})
        count = len(questions)
        print(f"📊 User {self.user_id}: Found {count} visible questions in list")
        return count
    
async def simulate_user_behavior(user_id: int, event_id: int):
    """Simulate a single user's behavior"""
    user = SimulatedUser(user_id, BASE_URL, event_id)
    
    try:
        # Create session
        await user.create_session()
        
        # Start listening to SSE in background
        sse_task = asyncio.create_task(user.listen_to_sse(duration=60))
        
        # Wait a bit before starting actions
        await asyncio.sleep(random.uniform(0.5, 2))
        
        # Submit 1-3 questions
        num_questions = random.randint(1, 3)
        for _ in range(num_questions):
            question = random.choice(SAMPLE_QUESTIONS)
            await user.submit_question(question)
            await asyncio.sleep(random.uniform(1, 3))
        
        # Get available question IDs
        question_uuids = await user.get_question_ids()
        
        # Random likes on available questions
        if question_uuids:
            num_likes = min(random.randint(2, 5), len(question_uuids))
            liked_questions = random.sample(question_uuids, num_likes)
            for question_uuid in liked_questions:
                await user.like_question(question_uuid)
                await asyncio.sleep(random.uniform(0.5, 2))
        
        # Wait for SSE task to complete
        await sse_task
        
    finally:
        await user.close()

async def run_load_test(num_users: int, event_id: int, 
                       include_moderator: bool = True,
                       moderator_username: str = "admin@example.com",
                       moderator_password: str = "admin_password"):
    """Run load test with multiple simulated users"""
    print(f"\n{'='*60}")
    print(f"🚀 STARTING LOAD TEST")
    print(f"{'='*60}")
    print(f"👥 Users: {num_users}")
    print(f"📍 Event ID: {event_id}")
    print(f"🌐 Target: {BASE_URL}/qa/event/{event_id}")
    print(f"⏰ Started at: {datetime.now()}\n")
    
    # Start moderator first
    if include_moderator:
        print("👨‍💼 Starting moderator simulation first...\n")
        await simulate_moderator_behavior(0, event_id, moderator_username, moderator_password)
    
    # Then start all regular users concurrently
    print(f"\n{'='*60}")
    print(f"👥 STARTING {num_users} CONCURRENT USERS")
    print(f"{'='*60}\n")
    
    user_tasks = [
        simulate_user_behavior(user_id=i, event_id=event_id)
        for i in range(1, num_users + 1)
    ]
    
    await asyncio.gather(*user_tasks)
    
    print(f"\n{'='*60}")
    print(f"✅ LOAD TEST COMPLETED")
    print(f"{'='*60}")
    print(f"⏰ Completed at: {datetime.now()}")
    print(f"📁 HTML responses saved in: tests/output/\n")

async def simulate_moderator_behavior(user_id: int, event_id: int, 
                                     moderator_username: str, 
                                     moderator_password: str):
    """Simulate moderator behavior"""
    moderator = SimulatedUser(user_id, BASE_URL, event_id)
    
    try:
        # Create session and login as moderator
        await moderator.create_session()
        
        print(f"\n{'='*60}")
        print(f"🔐 MODERATOR LOGIN SEQUENCE")
        print(f"{'='*60}")
        
        if not await moderator.login_as_moderator_test_mode(moderator_username, moderator_password):
            print(f"✗ Failed to login as moderator, aborting...")
            return
        
        # Verify moderator access
        print(f"\n🔍 VERIFYING MODERATOR ACCESS...")
        if not await moderator.verify_moderator_access():
            print(f"✗ Moderator access verification failed, aborting...")
            return
        
        # Small delay after login
        await asyncio.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"🎬 ACTIVATING Q&A SESSION")
        print(f"{'='*60}")
        
        # Activate the Q&A session (toggle it on)
        await moderator.activate_session(save_response=True)
        await asyncio.sleep(2)
        
        # Get initial moderator page state
        print(f"\n📄 Fetching initial moderator page...")
        mod_page = await moderator.get_moderator_page(save_response=True)
        
        if mod_page is None:
            print(f"✗ Could not access moderator page. Check authentication.")
            return
        
        print(f"\n{'='*60}")
        print(f"⏳ WAITING FOR USER QUESTIONS (10 seconds)")
        print(f"{'='*60}")
        
        # Wait for users to submit questions
        await asyncio.sleep(10)
        
        # Get available question UUIDs
        print(f"\n🔍 Fetching questions to moderate...")
        question_uuids = await moderator.get_question_ids()
        
        if not question_uuids:
            print("⚠️  No questions found yet. Waiting 5 more seconds...")
            await asyncio.sleep(5)
            question_uuids = await moderator.get_question_ids()
        
        if not question_uuids:
            print("⚠️  Still no questions found. Users may not have submitted yet.")
            return
        
        print(f"\n{'='*60}")
        print(f"📋 MODERATING {len(question_uuids)} QUESTIONS")
        print(f"{'='*60}")
        
        # Show some questions (toggle visibility to make them visible)
        questions_to_show = question_uuids[:min(5, len(question_uuids))]
        for i, question_uuid in enumerate(questions_to_show, 1):
            print(f"\n👁️  Showing question {i}/{len(questions_to_show)}: {question_uuid[:8]}...")
            await asyncio.sleep(random.uniform(2, 4))
            await moderator.show_question(question_uuid, save_response=True)
            
            # Get guest page after showing question to verify it appears
            await moderator.get_qa_page(save_response=True)
        
        # Mark some questions as answered
        if len(questions_to_show) >= 2:
            questions_to_answer = random.sample(questions_to_show, min(2, len(questions_to_show)))
            print(f"\n✅ Marking {len(questions_to_answer)} questions as answered...")
            for question_uuid in questions_to_answer:
                await asyncio.sleep(random.uniform(1, 2))
                await moderator.mark_answered(question_uuid, save_response=True)
        
        # Hide a couple questions if available
        if len(question_uuids) >= 2:
            questions_to_hide = random.sample(question_uuids, min(2, len(question_uuids)))
            print(f"\n🙈 Hiding {len(questions_to_hide)} questions...")
            for question_uuid in questions_to_hide:
                await asyncio.sleep(random.uniform(2, 3))
                await moderator.hide_question(question_uuid, save_response=True)
                await moderator.get_qa_page(save_response=True)
        
        print(f"\n{'='*60}")
        print(f"✅ MODERATOR SIMULATION COMPLETE")
        print(f"{'='*60}\n")
        
    finally:
        await moderator.close()

async def simulate_user_with_sse_and_polling(user_id: int, event_id: int):
    """Simulate a user with BOTH SSE listening AND periodic polling"""
    user = SimulatedUser(user_id, BASE_URL, event_id)
    
    try:
        await user.create_session()
        
        # Task 1: Listen to SSE stream (real-time updates)
        sse_task = asyncio.create_task(user.listen_to_sse_with_verification(duration=60))
        
        # Task 2: Periodically poll the questions list (verify SSE worked)
        async def periodic_verification():
            for i in range(6):  # Check 6 times over 60 seconds
                await asyncio.sleep(10)
                print(f"\n🔍 [{datetime.now()}] User {user_id}: Periodic verification #{i+1}")
                count = await user.count_visible_questions_in_list()
                visible_ids = await user.get_all_visible_question_ids()
        
        verify_task = asyncio.create_task(periodic_verification())
        
        # Task 3: User actions (submit, like)
        await asyncio.sleep(random.uniform(0.5, 2))
        for _ in range(random.randint(1, 3)):
            question = random.choice(SAMPLE_QUESTIONS)
            await user.submit_question(question)
            await asyncio.sleep(random.uniform(1, 3))
        
        # Wait for all tasks
        await asyncio.gather(sse_task, verify_task)
        
    finally:
        await user.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test question visibility flow')
    parser.add_argument('--num-users', '-n', type=int, default=5, 
                        help='Number of simulated users (default: 5)')
    parser.add_argument('--event-id', '-e', type=int, default=EVENT_ID,
                        help=f'Event ID to test (default: {EVENT_ID})')
    parser.add_argument('--username', '-u', type=str, default='testuser1',
                        help='Moderator username (default: testuser1)')
    parser.add_argument('--password', '-p', type=str, default='testpassword123',
                        help='Moderator password (default: testpassword123)')
    
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(run_load_test(args.num_users, args.event_id,
                              include_moderator=True,
                              moderator_username=args.username,
                              moderator_password=args.password))