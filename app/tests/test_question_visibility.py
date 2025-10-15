"""
Test question visibility flow - verifies that questions are properly hidden/shown
by moderators and that guests see the correct state.
"""
import asyncio
import random
from datetime import datetime
from bs4 import BeautifulSoup

from test_sse_load import (
    SimulatedUser,
    BASE_URL,
    EVENT_ID,
    SAMPLE_QUESTIONS
)

# Setup logging to file
import os
log_dir = "tests/output"
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"{log_dir}/test_visibility_{timestamp}.log"

# Override print to write to both console and file
original_print = print
def print(*args, **kwargs):
    """Print to both console and log file"""
    original_print(*args, **kwargs)
    with open(log_file, 'a', encoding='utf-8') as f:
        original_print(*args, **kwargs, file=f)

async def test_question_visibility_flow(moderator: SimulatedUser, guest: SimulatedUser, question_uuid: str) -> bool:
    """Test complete visibility flow for a single question"""
    print(f"\n{'─'*60}")
    print(f"🧪 TESTING QUESTION: {question_uuid[:8]}")
    print(f"{'─'*60}")
    
    # Step 1: Verify question is NOT visible to guest initially
    print(f"\n1️⃣ Checking guest view BEFORE moderator shows question...")
    guest_can_see_before = await guest.verify_question_visible_in_list(question_uuid)
    
    # Step 2: Verify moderator CAN see it in moderator view
    print(f"\n2️⃣ Checking moderator view (should always see all questions)...")
    mod_html = await moderator.get_qa_page(save_response=False, moderator=True)
    moderator_can_see = False
    if mod_html:
        soup = BeautifulSoup(mod_html, 'html.parser')
        mod_question_card = soup.find('div', attrs={'data-question-id': question_uuid})
        if mod_question_card:
            moderator_can_see = True
            print(f"✅ Moderator: Question {question_uuid[:8]} visible in moderator panel")
        else:
            print(f"❌ Moderator: Question {question_uuid[:8]} NOT in moderator panel (ERROR)")
    else:
        print(f"❌ Moderator: Could not fetch moderator page")
    
    if not moderator_can_see:
        print(f"❌ Cannot proceed - moderator cannot see question")
        return False
    
    # Step 3: Moderator toggles visibility (shows the question)
    print(f"\n3️⃣ Moderator showing question...")
    await moderator.show_question(question_uuid, save_response=False)
    await asyncio.sleep(1.5)  # Wait for SSE propagation
    
    # Step 4: Verify question IS NOW visible to guest
    print(f"\n4️⃣ Checking guest view AFTER moderator shows question...")
    guest_can_see_after = await guest.verify_question_visible_in_list(question_uuid)
    
    # Step 5: Results
    print(f"\n{'─'*60}")
    print(f"📊 RESULTS FOR QUESTION {question_uuid[:8]}:")
    print(f"   Guest view BEFORE: {'❌ Hidden (correct)' if not guest_can_see_before else '⚠️  Visible (unexpected!)'}")
    print(f"   Moderator view:     {'✅ Visible (correct)' if moderator_can_see else '❌ Hidden (ERROR)'}")
    print(f"   Guest view AFTER:  {'✅ Visible (correct)' if guest_can_see_after else '❌ Hidden (ERROR)'}")
    print(f"{'─'*60}")
    
    # Success if: hidden before, visible after
    success = (not guest_can_see_before) and guest_can_see_after
    
    if success:
        print(f"✅ TEST PASSED: Question correctly hidden → shown")
    else:
        print(f"❌ TEST FAILED: Expected hidden→visible, got {guest_can_see_before}→{guest_can_see_after}")
    
    return success


async def test_question_hide_flow(moderator: SimulatedUser, guest: SimulatedUser, question_uuid: str) -> bool:
    """Test hiding a visible question"""
    print(f"\n{'─'*60}")
    print(f"🧪 TESTING HIDE FLOW: {question_uuid[:8]}")
    print(f"{'─'*60}")
    
    # Step 1: Verify question IS visible to guest
    print(f"\n1️⃣ Verifying question is currently visible...")
    is_visible_before = await guest.verify_question_visible_in_list(question_uuid)
    
    if not is_visible_before:
        print(f"⚠️  Question not visible initially - cannot test hide flow")
        return False
    
    # Step 2: Moderator hides the question
    print(f"\n2️⃣ Moderator hiding question...")
    await moderator.hide_question(question_uuid, save_response=False)
    await asyncio.sleep(1.5)  # Wait for SSE propagation
    
    # Step 3: Verify question is NOW hidden from guest
    print(f"\n3️⃣ Checking guest view AFTER moderator hides question...")
    is_hidden_after = await guest.verify_question_hidden_on_page(question_uuid)
    
    # Results
    print(f"\n{'─'*60}")
    print(f"📊 HIDE TEST RESULTS:")
    print(f"   Before: {'✅ Visible' if is_visible_before else '❌ Hidden'}")
    print(f"   After:  {'✅ Hidden' if is_hidden_after else '❌ Still visible (ERROR)'}")
    print(f"{'─'*60}")
    
    success = is_visible_before and is_hidden_after
    
    if success:
        print(f"✅ HIDE TEST PASSED: Question correctly visible → hidden")
    else:
        print(f"❌ HIDE TEST FAILED")
    
    return success


async def test_question_answered_flow(moderator: SimulatedUser, guest: SimulatedUser, question_uuid: str) -> bool:
    """Test marking a question as answered"""
    print(f"\n{'─'*60}")
    print(f"🧪 TESTING ANSWERED STATUS: {question_uuid[:8]}")
    print(f"{'─'*60}")
    
    # Step 1: Verify question is visible to guest
    print(f"\n1️⃣ Verifying question is visible...")
    is_visible = await guest.verify_question_visible_in_list(question_uuid)
    
    if not is_visible:
        print(f"⚠️  Question not visible - showing it first...")
        await moderator.show_question(question_uuid, save_response=False)
        await asyncio.sleep(1)
        is_visible = await guest.verify_question_visible_in_list(question_uuid)
        if not is_visible:
            print(f"❌ Could not make question visible - aborting test")
            return False
    
    # Step 2: Check answered status before
    print(f"\n2️⃣ Checking answered status BEFORE...")
    is_answered_before = await guest.verify_question_answered_status(question_uuid)
    
    # Step 3: Moderator marks as answered
    print(f"\n3️⃣ Moderator marking question as answered...")
    await moderator.mark_answered(question_uuid, save_response=False)
    await asyncio.sleep(1.5)  # Wait for update
    
    # Step 4: Check answered status after
    print(f"\n4️⃣ Checking answered status AFTER...")
    is_answered_after = await guest.verify_question_answered_status(question_uuid)
    
    # Results
    print(f"\n{'─'*60}")
    print(f"📊 ANSWERED TEST RESULTS:")
    print(f"   Before: {'✅ Answered' if is_answered_before else '❌ Not answered'}")
    print(f"   After:  {'✅ Answered' if is_answered_after else '❌ Not answered (ERROR)'}")
    print(f"{'─'*60}")
    
    success = (not is_answered_before) and is_answered_after
    
    if success:
        print(f"✅ ANSWERED TEST PASSED: Question correctly marked as answered")
    else:
        print(f"❌ ANSWERED TEST FAILED")
    
    return success


async def run_comprehensive_visibility_test(
    moderator_username: str,
    moderator_password: str,
    num_users: int = 5,
    event_id: int = EVENT_ID,
):
    """Run comprehensive visibility testing with multiple users"""
    
    print(f"\n{'='*80}")
    print(f"🚀 COMPREHENSIVE QUESTION VISIBILITY TEST")
    print(f"{'='*80}")
    print(f"👥 Simulated users: {num_users}")
    print(f"📍 Event ID: {event_id}")
    print(f"🌐 Target: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now()}\n")
    
    # Create moderator and guest instances
    moderator = SimulatedUser(0, BASE_URL, event_id)
    guest = SimulatedUser(999, BASE_URL, event_id)
    
    try:
        # Setup sessions
        print(f"{'='*80}")
        print(f"🔧 SETUP PHASE")
        print(f"{'='*80}\n")
        
        await moderator.create_session()
        await guest.create_session()
        
        # Moderator login
        print(f"🔐 Logging in moderator...")
        if not await moderator.login_as_moderator_test_mode(moderator_username, moderator_password):
            print(f"❌ Moderator login failed - aborting")
            return
        
        if not await moderator.verify_moderator_access():
            print(f"❌ Moderator access verification failed - aborting")
            return
        
        # Activate Q&A session
        print(f"\n🎬 Activating Q&A session...")
        await moderator.activate_session(save_response=False)
        await asyncio.sleep(2)
        
        # Verify moderator page access
        mod_page = await moderator.get_qa_page(save_response=False, moderator=True)
        if not mod_page:
            print(f"❌ Cannot access moderator page - aborting")
            return
        
        # Start regular users to submit questions
        print(f"\n{'='*80}")
        print(f"👥 SIMULATING {num_users} USERS SUBMITTING QUESTIONS")
        print(f"{'='*80}\n")
        
        user_tasks = []
        for i in range(1, num_users + 1):
            user = SimulatedUser(i, BASE_URL, event_id)
            
            async def submit_questions(u):
                await u.create_session()
                for _ in range(random.randint(1, 2)):
                    question = random.choice(SAMPLE_QUESTIONS)
                    await u.submit_question(question)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                await u.close()
            
            user_tasks.append(submit_questions(user))
        
        await asyncio.gather(*user_tasks)
        
        # Wait for questions to be processed
        print(f"\n⏳ Waiting for questions to be processed...")
        await asyncio.sleep(3)
        
        # Get all submitted questions
        print(f"\n🔍 Fetching submitted questions...")
        question_uuids = await moderator.get_question_ids()
        
        if not question_uuids:
            print(f"⚠️  No questions found - waiting longer...")
            await asyncio.sleep(5)
            question_uuids = await moderator.get_question_ids()
        
        if not question_uuids:
            print(f"❌ No questions submitted - aborting test")
            return
        
        print(f"✅ Found {len(question_uuids)} questions to test\n")
        
        # Initial state check
        print(f"{'='*80}")
        print(f"📊 INITIAL STATE CHECK")
        print(f"{'='*80}\n")
        
        initial_guest_count = await guest.count_visible_questions_in_list()
        print(f"📊 Guest sees {initial_guest_count} questions initially (should be 0)")
        
        mod_html = await moderator.get_qa_page(save_response=False, moderator=True)
        if mod_html:
            soup = BeautifulSoup(mod_html, 'html.parser')
            mod_questions = soup.find_all('div', attrs={'data-question-id': True})
            print(f"📊 Moderator sees {len(mod_questions)} questions in panel")
        
        # Test visibility flow for each question
        print(f"\n{'='*80}")
        print(f"🧪 TESTING VISIBILITY FLOWS")
        print(f"{'='*80}")
        
        test_results = []
        questions_to_test = question_uuids[:min(5, len(question_uuids))]
        
        for i, question_uuid in enumerate(questions_to_test, 1):
            print(f"\n{'='*80}")
            print(f"TEST {i}/{len(questions_to_test)}: SHOW QUESTION")
            print(f"{'='*80}")
            
            result = await test_question_visibility_flow(moderator, guest, question_uuid)
            test_results.append({
                'uuid': question_uuid,
                'test': 'visibility',
                'passed': result
            })
            
            await asyncio.sleep(1)
        
        # Test hide functionality
        if any(r['passed'] for r in test_results):
            print(f"\n{'='*80}")
            print(f"🧪 TESTING HIDE FUNCTIONALITY")
            print(f"{'='*80}")
            
            # Pick a question that was successfully shown
            shown_questions = [r['uuid'] for r in test_results if r['passed']]
            if shown_questions:
                question_to_hide = shown_questions[0]
                hide_result = await test_question_hide_flow(moderator, guest, question_to_hide)
                test_results.append({
                    'uuid': question_to_hide,
                    'test': 'hide',
                    'passed': hide_result
                })
        
        # Test answered status
        if len([r for r in test_results if r['passed'] and r['test'] == 'visibility']) >= 2:
            print(f"\n{'='*80}")
            print(f"🧪 TESTING ANSWERED STATUS")
            print(f"{'='*80}")
            
            visible_questions = [r['uuid'] for r in test_results if r['passed'] and r['test'] == 'visibility']
            questions_to_mark = visible_questions[:min(2, len(visible_questions))]
            
            for question_uuid in questions_to_mark:
                answered_result = await test_question_answered_flow(moderator, guest, question_uuid)
                test_results.append({
                    'uuid': question_uuid,
                    'test': 'answered',
                    'passed': answered_result
                })
                await asyncio.sleep(1)
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"📊 FINAL TEST SUMMARY")
        print(f"{'='*80}\n")
        
        visibility_tests = [r for r in test_results if r['test'] == 'visibility']
        hide_tests = [r for r in test_results if r['test'] == 'hide']
        answered_tests = [r for r in test_results if r['test'] == 'answered']
        
        print(f"VISIBILITY TESTS (Show): {sum(1 for r in visibility_tests if r['passed'])}/{len(visibility_tests)} passed")
        for i, r in enumerate(visibility_tests, 1):
            status = "✅ PASS" if r['passed'] else "❌ FAIL"
            print(f"  {i}. {r['uuid'][:8]}... {status}")
        
        if hide_tests:
            print(f"\nHIDE TESTS: {sum(1 for r in hide_tests if r['passed'])}/{len(hide_tests)} passed")
            for r in hide_tests:
                status = "✅ PASS" if r['passed'] else "❌ FAIL"
                print(f"  • {r['uuid'][:8]}... {status}")
        
        if answered_tests:
            print(f"\nANSWERED TESTS: {sum(1 for r in answered_tests if r['passed'])}/{len(answered_tests)} passed")
            for r in answered_tests:
                status = "✅ PASS" if r['passed'] else "❌ FAIL"
                print(f"  • {r['uuid'][:8]}... {status}")
        
        total_passed = sum(1 for r in test_results if r['passed'])
        total_tests = len(test_results)
        
        print(f"\n{'─'*80}")
        print(f"OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
        print(f"{'─'*80}\n")
        
        # Final state
        final_guest_count = await guest.count_visible_questions_in_list()
        print(f"📊 Final guest view: {final_guest_count} visible questions")
        print(f"📊 Change from initial: {final_guest_count - initial_guest_count:+d}\n")
        
        print(f"{'='*80}")
        print(f"✅ TEST SUITE COMPLETED")
        print(f"⏰ Finished at: {datetime.now()}")
        print(f"{'='*80}\n")
        
    finally:
        await moderator.close()
        await guest.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test question visibility flow')
    parser.add_argument('--num-users', '-n', type=int, default=5, 
                        help='Number of simulated users (default: 5)')
    parser.add_argument('--event-id', '-e', type=int, default=EVENT_ID,
                        help=f'Event ID to test (default: {EVENT_ID})')
    parser.add_argument('--username', '-u', type=str, default='testuser',
                        help='Moderator username (default: testuser)')
    parser.add_argument('--password', '-p', type=str, default='testpass',
                        help='Moderator password (default: testpass)')
    
    args = parser.parse_args()
    
    # Run the comprehensive test
    asyncio.run(run_comprehensive_visibility_test(
        moderator_username=args.username,
        moderator_password=args.password,
        num_users=args.num_users,
        event_id=args.event_id,
    ))