from __future__ import print_function
import ccm
from ccm.lib.actr import *
import csv


# Define the ACT-R agent
class SleepFalseMemoryAgent(ACTR):
    goal = Buffer()  # Buffer for managing task goals
    retrieval = Buffer()  # Buffer for retrieval
    DM = Memory(retrieval)  # Declarative Memory Module

    # Sleep and wake parameters
    sleep_params = {"decay": 0.2, "noise": 0.1}  # Better retention
    wake_params = {"decay": 0.5, "noise": 0.3}  # Higher decay and noise

    def __init__(self, condition, studied_words):
        super(SleepFalseMemoryAgent, self).__init__()
        self.condition = condition
        self.studied_words = studied_words
        self.set_parameters()

    def set_parameters(self):
        params = self.sleep_params if self.condition == "sleep" else self.wake_params
        self.DM.baselevel_decay = params["decay"]
        self.DM.noise = params["noise"]

    def init(self):
        print("Initializing the SleepFalseMemoryAgent model.")

        # Add studied words to declarative memory
        for word in self.studied_words:
            self.DM.add("type:word content:{}".format(word))

        # Add a critical lure (if applicable)
        self.DM.add("type:critical_lure content:animal")  # Modify as needed

        # Set the initial goal
        self.goal.set("retrieve wordlist")

    # Retrieve studied words
    def retrieve_studied(self, goal="retrieve wordlist"):
        self.DM.request("type:word content:?content")
        self.goal.set("process retrieval")

    # Process retrieved word
    def process_retrieval(
        self, goal="process retrieval", retrieval="type:word content:?content"
    ):
        content = self.retrieval.chunk.content  # Get the content from the chunk
        print("Recalled: {}".format(content))
        self.goal.set("retrieve next")

    # Retrieve critical lure
    def retrieve_lure(self, goal="retrieve next"):
        self.DM.request("type:critical_lure content:?content")
        self.goal.set("process lure")

    # Process lure retrieval
    def process_lure(
        self, goal="process lure", retrieval="type:critical_lure content:?content"
    ):
        content = self.retrieval.chunk.content  # Get the content from the chunk
        print("Falsely recalled lure: {}".format(content))
        self.goal.set("done")

    # End simulation
    def finish(self, goal="done"):
        print("Simulation Complete!")
        self.stop()


# Environment definition
class MemoryEnvironment(ccm.Model):
    def init(self):
        print("Initializing MemoryEnvironment: {}".format(self.name))
        print("Type of self: {}".format(type(self)))


# Function to read studied words from CSV file
def read_studied_words(filename):
    studied_words = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row["studied_word"]
            recalled = row["studied_recalled"]
            if int(recalled) == 1:
                studied_words.append(word)
    return studied_words


# Running the simulation
def run_simulation(condition, filename):
    print("\nRunning simulation for {} group...\n".format(condition))

    # Read studied words from CSV
    studied_words = read_studied_words(filename)

    agent = SleepFalseMemoryAgent(condition, studied_words)
    environment = MemoryEnvironment()

    print("Assigning agent to environment...")
    environment.agent = agent

    ccm.log_everything(environment)

    # Do not call agent.start() explicitly

    print("Calling run on environment: {}".format(environment))
    environment.run()

    ccm.finished()


if __name__ == "__main__":
    csv_filename = "studied_final.csv"  # Replace with your CSV filename
    run_simulation("sleep", csv_filename)
    run_simulation("wake", csv_filename)
