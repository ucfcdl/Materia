from .module import ScoreModule

import os
import subprocess
import tempfile
class Pythond(ScoreModule):
	def check_answer(self,log):
		print("\n🚀🚀🚀 check_answer WAS CALLED! 🚀🚀🚀\n")
		print("HOLY SHIT WE ARE BEING CALLED AHAHAHAHAHAHAHAHAH")
		item_id = log.item_id if hasattr(log, "item_id") else log["item_id"]
		 # 🔴 Debugging: Print the item_id being searched
		print(f"🔍 Looking for question with ID: {item_id}")
		if item_id not in self.questions:
			print(f"❌ ERROR: Item ID '{item_id}' not found in self.questions!")
			print(f"Available IDs: {list(self.questions.keys())}")
			return 0  # Return 0 score if question is missing

		question = self.questions[item_id]  # Now it won't crash
		print(f"✅ Found question for Item ID: {item_id}")


		question = self.questions[item_id]
		user_code = log.text if hasattr(log, "text") else log["text"]
		#array of test cases with structure of {input: "...", "output": ".."}
		print(f"📝 Checking answer for Item ID: {item_id}")
		print(f"📜 User Code:\n{user_code}\n")
		testcases = question["answers"][0]["text"]

		tests_passed = 0

		for testcase in testcases:
			try:
				print(f"\n=== Running Test Case ===\nInput: {testcase['input']}")
				output = self.run_code(user_code, testcase["input"], timeout=2)
				print(f"Output: {output.strip()} | Expected: {testcase['output'].strip()}")
				if output.strip() == testcase["output"].strip():
					tests_passed += 1
			except Exception as e:
				print("we crashed?")
				pass

		total = len(testcases)
		if total ==0:
			return 100 #in the case there are no test cases I guess

		score = (tests_passed / total) * 100
		return score


	def run_code(self, code, input_data, timeout=2):
		"""Run the code in a sandbox subprocess, we could try docker containers or other stuff."""
		# Make a temp file to write code
		with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
			tmp.write(code)
			tmp.flush()
			tmp_name = tmp.name

		try:
			# Ensure input_data is a string
			if isinstance(input_data, bytes):
				input_data = input_data.decode("utf-8")

			# Run a subprocess to execute tmp file
			print(f"\n=== Running Code ===\n{code}\n")
			result = subprocess.run(
				["python3", tmp_name],
				input=input_data,  # No .encode() needed
				capture_output=True,
				text=True,
				timeout=timeout
			)
			os.remove(tmp_name)

			# If code had a runtime error
			if result.returncode != 0:
				print(f"Runtime Error: {result.stderr}")
				raise Exception("Runtime error: " + result.stderr)

			print(f"Program Output:\n{result.stdout}")
			return result.stdout

		except subprocess.TimeoutExpired:
			# Timed out => raise exception
			os.remove(tmp_name)
			print("Error: Time Limit Exceeded")
			raise Exception("Time Limit Exceeded")

		except Exception as e:
			os.remove(tmp_name)
			print(f"Unexpected Error: {e}")
			raise e

