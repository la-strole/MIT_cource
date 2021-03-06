# Problem Set 3: Simulating the Spread of Disease and Virus Population Dynamics 

import random
import pylab

# from ps3b_precompiled_36 import *

''' 
Begin helper code
'''


class NoChildException(Exception):
    """
    NoChildException is raised by the reproduce() method in the SimpleVirus
    and ResistantVirus classes to indicate that a virus particle does not
    reproduce. You can use NoChildException as is, you do not need to
    modify/add any code.
    """


'''
End helper code
'''


#
# PROBLEM 1
#
class SimpleVirus(object):
    """
    Representation of a simple virus (does not model drug effects/resistance).
    """

    def __init__(self, maxBirthProb, clearProb):
        """
        Initialize a SimpleVirus instance, saves all parameters as attributes
        of the instance.        
        maxBirthProb: Maximum reproduction probability (a float between 0-1)        
        clearProb: Maximum clearance probability (a float between 0-1).
        """

        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb

    def getMaxBirthProb(self):
        """
        Returns the max birth probability.
        """
        return self.maxBirthProb

    def getClearProb(self):
        """
        Returns the clear probability.
        """
        return self.clearProb

    def doesClear(self):
        """ Stochastically determines whether this virus particle is cleared from the
        patient's body at a time step. 
        returns: True with probability self.getClearProb and otherwise returns
        False.
        """
        # random.seed(0)
        return random.random() <= self.clearProb


    def reproduce(self, popDensity):
        """
        Stochastically determines whether this virus particle reproduces at a
        time step. Called by the update() method in the Patient and
        TreatedPatient classes. The virus particle reproduces with probability
        self.maxBirthProb * (1 - popDensity).
        
        If this virus particle reproduces, then reproduce() creates and returns
        the instance of the offspring SimpleVirus (which has the same
        maxBirthProb and clearProb values as its parent).         

        popDensity: the population density (a float), defined as the current
        virus population divided by the maximum population.         
        
        returns: a new instance of the SimpleVirus class representing the
        offspring of this virus particle. The child should have the same
        maxBirthProb and clearProb values as this virus. Raises a
        NoChildException if this virus particle does not reproduce.               
        """

        if random.random() <= self.maxBirthProb * (1 - popDensity):
            return SimpleVirus(self.getMaxBirthProb(), self.getClearProb())
        raise NoChildException


class Patient(object):
    """
    Representation of a simplified patient. The patient does not take any drugs
    and his/her virus populations have no drug resistance.
    """

    def __init__(self, viruses, maxPop):
        """
        Initialization function, saves the viruses and maxPop parameters as
        attributes.

        viruses: the list representing the virus population (a list of
        SimpleVirus instances)

        maxPop: the maximum virus population for this patient (an integer)
        """

        assert type(viruses) == list
        assert type(maxPop) == int
        for item in viruses:
            assert isinstance(item, SimpleVirus)

        self.viruses = viruses.copy()
        self.maxPop = maxPop

    def getViruses(self):
        """
        Returns the viruses in this Patient.
        """
        return self.viruses

    def getMaxPop(self):
        """
        Returns the max population.
        """
        return self.maxPop

    def getTotalPop(self):
        """
        Gets the size of the current total virus population. 
        returns: The total virus population (an integer)
        """

        return len(self.viruses)

    def update(self):
        """
        Update the state of the virus population in this patient for a single
        time step. update() should execute the following steps in this order:
        
        - Determine whether each virus particle survives and updates the list
        of virus particles accordingly.   
        
        - The current population density is calculated. This population density
          value is used until the next call to update()
        
        - Based on this value of population density, determine whether each 
          virus particle should reproduce and add offspring virus particles to 
          the list of viruses in this patient.                    

        returns: The total virus population at the end of the update (an
        integer)
        """
        survive_viruses = [alive_virus for alive_virus in self.getViruses() if not alive_virus.doesClear()]
        population_density = len(survive_viruses) / self.getMaxPop()
        offspring = []
        for virus in survive_viruses:
            try:
                virus.reproduce(population_density)
                offspring.append(virus)
            except NoChildException:
                continue

        self.viruses = survive_viruses + offspring
        return len(self.getViruses())


#
# PROBLEM 2
#
def simulationWithoutDrug(numViruses, maxPop, maxBirthProb, clearProb,
                          numTrials):
    """
    Run the simulation and plot the graph for problem 3 (no drugs are used,
    viruses do not have any drug resistance).    
    For each of numTrials trial, instantiates a patient, runs a simulation
    for 300 timesteps, and plots the average virus population size as a
    function of time.

    numViruses: number of SimpleVirus to create for patient (an integer)
    maxPop: maximum virus population for patient (an integer)
    maxBirthProb: Maximum reproduction probability (a float between 0-1)        
    clearProb: Maximum clearance probability (a float between 0-1)
    numTrials: number of simulation runs to execute (an integer)
    """

    assert type(numViruses) == int
    assert type(maxPop) == int
    assert type(maxBirthProb) == float and 0 <= maxBirthProb <= 1
    assert type(clearProb) == float and 0 <= clearProb <= 1
    assert type(numTrials) == int

    timesteps = 300

    avg_viruses_count = [0] * timesteps
    for trial in range(numTrials):
        print('trial number = ', trial)
        viruses_at_begin = [SimpleVirus(maxBirthProb, clearProb) for i in range(numViruses)]
        patient = Patient(viruses_at_begin, maxPop)
        viruses_count = []
        for time_step in range(timesteps):
            viruses_count.append(patient.update())
            # print('virus count = ', viruses_count[-1])
        avg_viruses_count = [avg_viruses_count[i] + (viruses_count[i] / numTrials) for i in range(timesteps)]

    pylab.plot(avg_viruses_count, label='SimpleVirus')
    pylab.title("SimpleVirus simulation")
    pylab.xlabel("Time Steps")
    pylab.ylabel("Average Virus Population")
    pylab.legend(loc="best")
    pylab.show()


#
# PROBLEM 3
#
class ResistantVirus(SimpleVirus):
    """
    Representation of a virus which can have drug resistance.
    """

    def __init__(self, maxBirthProb, clearProb, resistances, mutProb):
        """
        Initialize a ResistantVirus instance, saves all parameters as attributes
        of the instance.

        maxBirthProb: Maximum reproduction probability (a float between 0-1)

        clearProb: Maximum clearance probability (a float between 0-1).

        resistances: A dictionary of drug names (strings) mapping to the state
        of this virus particle's resistance (either True or False) to each drug.
        e.g. {'guttagonol':False, 'srinol':False}, means that this virus
        particle is resistant to neither guttagonol nor srinol.

        mutProb: Mutation probability for this virus particle (a float). This is
        the probability of the offspring acquiring or losing resistance to a drug.
        """
        SimpleVirus.__init__(self, maxBirthProb, clearProb)
        assert type(resistances) == dict
        for key in resistances.keys():
            assert type(key) == str
        for value in resistances.values():
            assert type(value) == bool
        assert type(mutProb) == float and 0 <= mutProb <= 1

        self.resistance = resistances
        self.mutProb = mutProb

    def getResistances(self):
        """
        Returns the resistances for this virus.
        """
        return self.resistance

    def getMutProb(self):
        """
        Returns the mutation probability for this virus.
        """
        return self.mutProb

    def isResistantTo(self, drug):
        """
        Get the state of this virus particle's resistance to a drug. This method
        is called by getResistPop() in TreatedPatient to determine how many virus
        particles have resistance to a drug.

        drug: The drug (a string)

        returns: True if this virus instance is resistant to the drug, False
        otherwise.
        """

        assert type(drug) == str
        # assert drug in self.getResistances().keys()
        if drug in self.getResistances().keys():
            return self.getResistances()[drug]
        return False

    def reproduce(self, popDensity, activeDrugs):
        """
        Stochastically determines whether this virus particle reproduces at a
        time step. Called by the update() method in the TreatedPatient class.

        A virus particle will only reproduce if it is resistant to ALL the drugs
        in the activeDrugs list. For example, if there are 2 drugs in the
        activeDrugs list, and the virus particle is resistant to 1 or no drugs,
        then it will NOT reproduce.

        Hence, if the virus is resistant to all drugs
        in activeDrugs, then the virus reproduces with probability:

        self.maxBirthProb * (1 - popDensity).

        If this virus particle reproduces, then reproduce() creates and returns
        the instance of the offspring ResistantVirus (which has the same
        maxBirthProb and clearProb values as its parent). The offspring virus
        will have the same maxBirthProb, clearProb, and mutProb as the parent.

        For each drug resistance trait of the virus (i.e. each key of
        self.resistances), the offspring has probability 1-mutProb of
        inheriting that resistance trait from the parent, and probability
        mutProb of switching that resistance trait in the offspring.

        For example, if a virus particle is resistant to guttagonol but not
        srinol, and self.mutProb is 0.1, then there is a 10% chance that
        that the offspring will lose resistance to guttagonol and a 90%
        chance that the offspring will be resistant to guttagonol.
        There is also a 10% chance that the offspring will gain resistance to
        srinol and a 90% chance that the offspring will not be resistant to
        srinol.

        popDensity: the population density (a float), defined as the current
        virus population divided by the maximum population

        activeDrugs: a list of the drug names acting on this virus particle
        (a list of strings).

        returns: a new instance of the ResistantVirus class representing the
        offspring of this virus particle. The child should have the same
        maxBirthProb and clearProb values as this virus. Raises a
        NoChildException if this virus particle does not reproduce.
        """
        # assert type(popDensity) == float
        assert type(activeDrugs) == list
        if activeDrugs:
            for drug in activeDrugs:
                assert drug in self.getResistances().keys()

        if all([self.getResistances()[drug] for drug in activeDrugs]):
            if random.random() <= self.maxBirthProb * (1 - popDensity):
                resistance_child = self.getResistances().copy()
                for drug in resistance_child.keys():
                    if random.random() <= self.mutProb:
                        resistance_child[drug] = not resistance_child[drug]
                return ResistantVirus(self.getMaxBirthProb(), self.getClearProb(), resistance_child, self.getMutProb())

        raise NoChildException


class TreatedPatient(Patient):
    """
    Representation of a patient. The patient is able to take drugs and his/her
    virus population can acquire resistance to the drugs he/she takes.
    """

    def __init__(self, viruses, maxPop):
        """
        Initialization function, saves the viruses and maxPop parameters as
        attributes. Also initializes the list of drugs being administered
        (which should initially include no drugs).

        viruses: The list representing the virus population (a list of
        virus instances)

        maxPop: The  maximum virus population for this patient (an integer)
        """
        assert type(viruses) == list
        for virus in viruses:
            assert isinstance(virus, ResistantVirus)
        self.viruses = viruses
        self.maxPop = maxPop
        self.drugs_list = []

    def addPrescription(self, newDrug):
        """
        Administer a drug to this patient. After a prescription is added, the
        drug acts on the virus population for all subsequent time steps. If the
        newDrug is already prescribed to this patient, the method has no effect.

        newDrug: The name of the drug to administer to the patient (a string).

        postcondition: The list of drugs being administered to a patient is updated
        """

        assert type(newDrug) == str
        if newDrug not in self.getPrescriptions():
            self.getPrescriptions().append(newDrug)

    def getPrescriptions(self):
        """
        Returns the drugs that are being administered to this patient.

        returns: The list of drug names (strings) being administered to this
        patient.
        """

        return self.drugs_list

    def getResistPop(self, drugResist):
        """
        Get the population of virus particles resistant to the drugs listed in
        drugResist.

        drugResist: Which drug resistances to include in the population (a list
        of strings - e.g. ['guttagonol'] or ['guttagonol', 'srinol'])

        returns: The population of viruses (an integer) with resistances to all
        drugs in the drugResist list.
        """

        def virus_drugResist(virus):
            """
            return True if virus resist to all drugs from drugResist
            else return false
            virus - instance of ResistantVirus()
            """
            assert isinstance(virus, ResistantVirus)

            for drug in drugResist:
                if drug in virus.getResistances().keys() and virus.getResistances()[drug]:
                    continue
                else:
                    return False
            return True

        resistant_number = 0
        for virus in self.getViruses():
            if virus_drugResist(virus):
                resistant_number += 1

        return resistant_number

    def update(self):
        """
        Update the state of the virus population in this patient for a single
        time step. update() should execute these actions in order:

        - Determine whether each virus particle survives and update the list of
          virus particles accordingly

        - The current population density is calculated. This population density
          value is used until the next call to update().

        - Based on this value of population density, determine whether each
          virus particle should reproduce and add offspring virus particles to
          the list of viruses in this patient.
          The list of drugs being administered should be accounted for in the
          determination of whether each virus particle reproduces.

        returns: The total virus population at the end of the update (an
        integer)
        """

        survive_viruses = [alive_virus for alive_virus in self.getViruses() if not alive_virus.doesClear()]
        population_density = len(survive_viruses) / self.getMaxPop()
        offspring = []
        for virus in survive_viruses:
            try:
                virus.reproduce(population_density, self.getPrescriptions())
                offspring.append(virus)
            except NoChildException:
                continue

        self.viruses = survive_viruses + offspring
        return len(self.getViruses())


#
# PROBLEM 4
#
def simulationWithDrug(numViruses, maxPop, maxBirthProb, clearProb, resistances,
                       mutProb, numTrials):
    """
    Runs simulations and plots graphs for problem 5.

    For each of numTrials trials, instantiates a patient, runs a simulation for
    150 timesteps, adds guttagonol, and runs the simulation for an additional
    150 timesteps.  At the end plots the average virus population size
    (for both the total virus population and the guttagonol-resistant virus
    population) as a function of time.

    numViruses: number of ResistantVirus to create for patient (an integer)
    maxPop: maximum virus population for patient (an integer)
    maxBirthProb: Maximum reproduction probability (a float between 0-1)        
    clearProb: maximum clearance probability (a float between 0-1)
    resistances: a dictionary of drugs that each ResistantVirus is resistant to
                 (e.g., {'guttagonol': False})
    mutProb: mutation probability for each ResistantVirus particle
             (a float between 0-1). 
    numTrials: number of simulation runs to execute (an integer)
    
    """

    assert type(numViruses) == int and numViruses >= 0
    assert type(maxPop) == int
    assert type(maxBirthProb) == float and 0 <= maxBirthProb <= 1
    assert type(clearProb) == float and 0 <= clearProb <= 1
    assert type(resistances) == dict
    assert type(mutProb) == float and 0 <= mutProb <= 1
    assert type(numTrials) == int and 0 <= numTrials

    steps_number = 150

    viruses = [ResistantVirus(maxBirthProb, clearProb, resistances, mutProb) for virus in range(numViruses)]
    total = [0] * 2 * steps_number
    v_resist = total.copy()
    for trial in range(numTrials):
        print('trial ', trial)
        patient = TreatedPatient(viruses, maxPop)
        for step in range(steps_number):
            total[step] += patient.update() / numTrials
            v_resist[step] += patient.getResistPop(['guttagonol']) / numTrials
        patient.addPrescription('guttagonol')
        for step in range(steps_number):
            total[steps_number + step] += patient.update() / numTrials
            v_resist[steps_number + step] += patient.getResistPop(['guttagonol']) / numTrials
    pylab.plot(total, label='ResistantVirus')
    pylab.plot(v_resist, label='number of viruses resistant to guttagonol')
    pylab.title("ResistantVirus simulation")
    pylab.xlabel("Time Steps")
    pylab.ylabel("Average Virus Population")
    pylab.legend(loc="best")
    pylab.show()


# simulationWithoutDrug(numViruses=100, maxPop=1000, maxBirthProb=0.5, clearProb=0.5, numTrials=100)
simulationWithDrug(numViruses=100, maxPop=1000, maxBirthProb=0.1, clearProb=0.05, resistances={'guttagonol': False},
                   mutProb=0.005, numTrials=100)
