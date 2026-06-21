def print_manual_test_instructions():
    instructions = """
============================================================
              MEMORA STREAMLIT UI MANUAL TEST MANUAL
============================================================

To perform manual UI testing, follow these verification steps:

1. Setup:
   - Ensure the FastAPI backend is running: `uvicorn app.api:app --port 8000`
   - Launch Streamlit: `streamlit run frontend/app.py`
   - Open your browser to the URL shown in Streamlit's command output.

2. Scenario A Verification (Job and City Update):
   - Click "1. 'I work at Google in San Francisco'" in the sidebar.
   - Verify:
     - The chat message appears.
     - The assistant confirms storing the facts.
     - Under "Active Facts", "Employer" maps to "Google", and "City" maps to "San Francisco" as green badges.
   - Click "2. 'I just moved to New York for my new job at Meta'".
   - Verify:
     - Assistant confirms updates.
     - "Active Facts" now shows "Employer = Meta" and "City = New York".
     - Click "Version History". Verify v1 of Employer (Google) and City (SF) exist as grey 'superseded' badges.
     - Click "Audit Log Console" and verify "SUPERSEDED" and "CREATED" log rows are populated.

3. Scenario B Verification (Dog Name Recall):
   - Click "1. 'My dog's name is Max'". Verify active dog name is recorded.
   - Click "2. 'What's my dog's name?'". Verify the chat assistant answers "Max" correctly.

4. Scenario C Verification (Stable Fact Birthday Conflict):
   - Click "1. 'My birthday is July 15th'". Verify birthday active memory.
   - Click "2. 'My birthday is July 20th'".
   - Verify:
     - The chat assistant flags a warning/clarification request.
     - Under "Active Facts", birthday remains "July 15" (active).
     - Under "Version History", v2 of birthday exists with a red 'disputed' badge and resolution note: 'Stable property... cannot have conflicting values...'.
     - Under "Audit Log Console", a row with status '[DISPUTED]' is visible.

5. Scenario D Verification (Preference Reversals):
   - Click "1. 'I hate spicy food'". Verify active preference is stored.
   - Click "2. 'I love spicy food actually'".
   - Verify:
     - The active preference is updated.
     - Old preference is superseded.

6. Clear Memory:
   - Click "Clear User Memory" button.
   - Verify that the chat log is reset and all memory tabs show empty info logs.
============================================================
"""
    print(instructions)

if __name__ == "__main__":
    print_manual_test_instructions()
