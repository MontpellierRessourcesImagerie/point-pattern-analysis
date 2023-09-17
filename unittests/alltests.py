import unittest
import sys
import fr.cnrs.mri.cialib.unittests.generatortest as generatortest
import fr.cnrs.mri.cialib.unittests.imagingtest as imagingtest


suites = []
suites.append(unittest.defaultTestLoader.loadTestsFromModule(generatortest))
suites.append(unittest.defaultTestLoader.loadTestsFromModule(imagingtest))


print(suites)
allTests = unittest.TestSuite()
def main(): 
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    for suite in suites:
        allTests.addTests(suite)
    runner.run(allTests)



if __name__ == "__main__":
    main()