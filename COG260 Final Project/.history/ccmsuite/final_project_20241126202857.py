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
        super().__init__()
        self.condition = condition
        self.set_parameters()

    def set_parameters(self):
        params = self.sleep_params if self.condition == "sleep" else self.wake_params
        self.DM.baselevel_decay = params["decay"]
        self.DM.noise = params["noise"]

    def start(self):  # Add the required 'self' argument here
        print("Starting the SleepFalseMemoryAgent model.")

    def init(self):
        # Studied words and critical lures
        self.DM.add("type:word content:cat")
        self.DM.add("type:word content:dog")
        self.DM.add("type:word content:mouse")
        self.DM.add("type:critical_lure content:animal")

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
        print(f"Recalled: {content}")
        self.goal.set("retrieve next")

    # Retrieve critical lure
    def retrieve_lure(self, goal="retrieve next"):
        self.DM.request("type:critical_lure content:?content")
        self.goal.set("process lure")

    # Process lure retrieval
    def process_lure(
        self, goal="process lure", retrieval="type:critical_lure content:?content"
    ):
        print(f"Falsely recalled lure: {content}")
        self.goal.set("done")

    # End simulation
    def finish(self, goal="done"):
        print("Simulation Complete!")
        self.stop()


# Environment definition
class MemoryEnvironment(ccm.Model):
    def start(self):  # Add the required 'self' argument here
        print("Starting the MemoryEnvironment.")


# Running the simulation
def run_simulation(condition):
    print(f"\nRunning simulation for {condition} group...\n")
    agent = SleepFalseMemoryAgent(condition)
    environment = MemoryEnvironment()
    environment.agent = agent

    ccm.log_everything(environment)
    environment.run()
    ccm.finished()


if __name__ == "__main__":
    run_simulation("sleep")
    run_simulation("wake")
