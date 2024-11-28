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

    def init():
        # Studied words and critical lures
        DM.add("type:word content:cat")
        DM.add("type:word content:dog")
        DM.add("type:word content:mouse")
        DM.add("type:critical_lure content:animal")

        # Set the initial goal
        goal.set("retrieve wordlist")

    # Retrieve studied words
    def retrieve_studied(goal="retrieve wordlist"):
        DM.request("type:word content:?content")
        goal.set("process retrieval")

    # Process retrieved word
    def process_retrieval(
        goal="process retrieval", retrieval="type:word content:?content"
    ):
        print(f"Recalled: {content}")
        goal.set("retrieve next")

    # Retrieve critical lure
    def retrieve_lure(goal="retrieve next"):
        DM.request("type:critical_lure content:?content")
        goal.set("process lure")

    # Process lure retrieval
    def process_lure(
        goal="process lure", retrieval="type:critical_lure content:?content"
    ):
        print(f"Falsely recalled lure: {content}")
        goal.set("done")

    # End simulation
    def finish(goal="done"):
        print("Simulation Complete!")
        self.stop()


# Environment definition
class MemoryEnvironment(ccm.Model):
    pass


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
