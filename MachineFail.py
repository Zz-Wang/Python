"""
Job excution example

Covers:

- Interrupts


Scenario:
  A ssr_hw has *n* identical machines. A stream of jobs (enough to
  keep the machines busy) arrives. Each machine breaks down
  periodically. Repairs are carried out with exponential amount of time.
  Broken machines preempt theses tasks. The workshop works continuously.

"""

import random
import simpy


RANDOM_SEED = 42

PT_MEAN = 240.0         # Avg. processing time in minutes
PT_SIGMA = 60.0         # Sigma of processing time


MTTF = 300.0           # Mean time to failure in minutes
BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
REPAIR_TIME_MEAN = 60.0     # Time it takes to repair a machine in minutes
OTHER_JOB_TIME_MEAN = 30.0

NUM_MACHINES = 3      # Number of machines in the machine shop
DAYS = 1              # Simulation time in weeks
SIM_TIME = 24 * 60  # Simulation time in minutes


def time_per_part():
    """Return actual processing time for a concrete part."""
    return random.normalvariate(PT_MEAN, PT_SIGMA)


def time_to_failure():
    """Return time until next failure for a machine."""
    return random.expovariate(BREAK_MEAN)

def time_to_otherjob():
    """Return time until next other job for the repairman."""
    return random.expovariate(OTHER_JOB_TIME_MEAN)

def time_to_repair():
    """Return time until next other job for the repairman."""
    return random.expovariate(REPAIR_TIME_MEAN)

class Machine(object):
    """A machine produces parts and my get broken every now and then.

    If it breaks, it requests a *repairman* and continues the production
    after the it is repaired.

    A machine has a *name* and a numberof *parts_made* thus far.

    """
    def __init__(self, env, name, repair):
        self.env = env
        self.name = name
        self.parts_made = 0
        self.broken = False

        # Start "working" and "break_machine" processes for this machine.
        self.process = env.process(self.working(name, repair))
        print('%s arriving at ssr_hw at %.1f' % (name, env.now))
        env.process(self.break_machine())

    def working(self, name, repair):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairman when this happens.

        """
        while True:
            # Start making a new part
            done_in = time_per_part()
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now
                    yield self.env.timeout(done_in)
                    done_in = 0  # Set to 0 to exit while loop.

                except simpy.Interrupt:
                    self.broken = True
                    done_in -= self.env.now - start  # How much time left?

                    # Request a repairman. This will preempt its "other_job".
                    with repairman.request(priority=1) as req:
                        yield req
                        yield self.env.timeout(time_to_repair())

                    self.broken = False

            # Part is done.
            self.parts_made += 1
            print('%s finished testing in %.1f minutes.' % (name,
                                                          env.now - start))

    def break_machine(self):
        """Break the machine every now and then."""
        while True:
            yield self.env.timeout(time_to_failure())
            if not self.broken:
                # Only break the machine if it is currently working.
                self.process.interrupt()


def other_jobs(env, repairman):
    """The repairman's other (unimportant) job."""
    while True:
        # Start a new job
        done_in = time_to_otherjob()
        while done_in:
            # Retry the job until it is done.
            # It's priority is lower than that of machine repairs.
            with repairman.request(priority=2) as req:
                yield req
                try:
                    start = env.now
                    yield env.timeout(done_in)
                    done_in = 0
                except simpy.Interrupt:
                    done_in -= env.now - start


# Setup and start the simulation
print('Machine shop')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
repairman = simpy.PreemptiveResource(env, capacity=1)
machines = [Machine(env, 'Machine %d' % i, repairman)
        for i in range(NUM_MACHINES)]
env.process(other_jobs(env, repairman))

# Execute!
env.run(until=SIM_TIME)

# Analyis/results
print('Machine shop results after %s days' % DAYS)
for machine in machines:
    print('%s made %d parts.' % (machine.name, machine.parts_made))
