from __future__ import print_function
import ccm
from ccm.lib.actr import *


# Define the ACT-R agent
class SleepFalseMemoryAgent(ACTR):
    goal = Buffer()  # Buffer for managing task goals
    retrieval = Buffer()  # Buffer for retrieval
    DM = Memory(retrieval)  # Declarative Memory Module

    # Sleep and wake parameters
    sleep_params = {"decay": 0.2, "noise": 0.1}  # Better retention
    wake_params = {"decay": 0.5, "noise": 0.3}  # Higher decay and noise

    def __init__(self, condition):
        super(SleepFalseMemoryAgent, self).__init__()
        self.condition = condition
        self.set_parameters()

    def set_parameters(self):
        params = self.sleep_params if self.condition == "sleep" else self.wake_params
        self.DM.baselevel_decay = params["decay"]
        self.DM.noise = params["noise"]

    def init(self):
        print("Initializing the SleepFalseMemoryAgent model.")

        # Studied words and critical lures
        self.DM.add("type:word content:cat")
        self.DM.add("type:word content:dog")
        self.DM.add("type:word content:mouse")
        self.DM.add("type:critical_lure content:animal")

        # Set the initial goal
        self.goal.set("retrieve wordlist")

    def start(self):
        super(SleepFalseMemoryAgent, self).start()
        self.init()

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

    def start(self):
        self.init()


# Running the simulation
def run_simulation(condition):
    print("\nRunning simulation for {} group...\n".format(condition))
    agent = SleepFalseMemoryAgent(condition)
    environment = MemoryEnvironment()

    print("Assigning agent to environment...")
    environment.agent = agent

    ccm.log_everything(environment)

    print("Calling run on environment: {}".format(environment))
    environment.run()

    ccm.finished()


if __name__ == "__main__":
    run_simulation("sleep")
    run_simulation("wake")
