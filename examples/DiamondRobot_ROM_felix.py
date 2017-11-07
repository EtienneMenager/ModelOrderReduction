 
import Sofa

import os
pathSceneFile = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(os.path.abspath(__file__))+'/Mesh/'
meshRobot=path+'myDiamondQuiteFine.vtu'

modesRobot=pathSceneFile + '/modes_Options/modes_DiamondQuiteFine.txt'
RIDFile = pathSceneFile + '/ECSWdata_stored/reducedIntegrationDomain_DiamondExhaustiveQuite31modes.txt'
weightsFile = pathSceneFile + '/ECSWdata_stored/weights_DiamondExhaustiveQuite31modes.txt'
listActiveNodesFile = pathSceneFile + '/ECSWdata_stored/listActiveNodes_DiamondExhaustiveQuite31Modes.txt'

nbModes = 31
performECSWBool = "true"

modesPositionStr = '0'
for i in range(1,nbModes):
    modesPositionStr = modesPositionStr + ' 0'


def createScene(rootNode):

 	  # Root node
                rootNode.findData('dt').value=1
                rootNode.findData('gravity').value='0 0 -9810'
                rootNode.createObject('VisualStyle', displayFlags='showCollision showVisualModels showForceFields showInteractionForceFields hideCollisionModels hideBoundingCollisionModels hideWireframe')
 
		#Required plugin
                rootNode.createObject('RequiredPlugin', pluginName='SoftRobots')
  
                rootNode.createObject('FreeMotionAnimationLoop')
                rootNode.createObject('CollisionPipeline', verbose='0')
                rootNode.createObject('BruteForceDetection', name='N2')
                rootNode.createObject('CollisionResponse', response='FrictionContact')
                rootNode.createObject('LocalMinDistance', name="Proximity", alarmDistance='0.02', contactDistance='0.01')
		rootNode.createObject('QPInverseProblemSolver', name="QP", printLog='0')


                #goal
                goal = rootNode.createChild('goal')
                goal.createObject('EulerImplicit', firstOrder='1')
                goal.createObject('CGLinearSolver', iterations='100',threshold="1e-5", tolerance="1e-5")
                goal.createObject('MechanicalObject', name='goalMO', position='0 0 125')
                goal.createObject('Sphere', radius='5', group='1')
                goal.createObject('UncoupledConstraintCorrection')


		solverNode = rootNode.createChild('solverNode')
		solverNode.createObject('EulerImplicitSolver', printLog = '1')
                solverNode.createObject('ShewchukPCGLinearSolver', iterations="1", name="linearsolver", tolerance="1e-5", preconditioners="ldlsolveur", use_precond="true", update_step="1")
                solverNode.createObject('SparseLDLSolver', name="ldlsolveur")
                #solverNode.createObject('SparsePARDISOSolver', name="ldlsolveur")
	        solverNode.createObject('GenericConstraintCorrection', solverName='ldlsolveur')
                #feuille
                
		feuilleMOR = solverNode.createChild('feuilleMOR')
		feuilleMOR.createObject('MechanicalObject', template='Vec1d',name='alpha', position=modesPositionStr,printLog="1")
		feuille = feuilleMOR.createChild('feuille')
                feuille.createObject('MeshVTKLoader', name="loader", filename=meshRobot) 
                feuille.createObject('Mesh',name='meshInput', src="@loader")
                feuille.createObject('MechanicalObject', name="tetras", template="Vec3d", showIndices="false", showIndicesScale="4e-5", rx="90", dz="35",printLog="1")
		feuille.createObject('ModelOrderReductionMapping', input='@../alpha', output='@./tetras',modesPath=modesRobot, listActiveNodesPath="listActiveNodes_Diamond.txt",performECSW="false", mapForces = '1')                
		feuille.createObject('UniformMass',name="diamondMass", totalmass="0.5",printLog="1")
		feuille.createObject('HyperReducedTetrahedronFEMForceField', youngModulus="450", poissonRatio="0.45", name='HyperReducedFF', src="@meshInput", prepareECSW="false", performECSW=performECSWBool, nbModes="15", modesPath=modesRobot, RIDPath=RIDFile, weightsPath=weightsFile,nbTrainingSet="200",printLog="1") 
                feuille.createObject('BoxROI', name="boxROI", box="-15 -15 -40  15 15 10", drawBoxes="true")
		 
		solverNode.createObject('MappedMatrixForceField', template='Vec1d,Vec1d', object1='@./feuilleMOR/alpha', object2='@./feuilleMOR/alpha', mappedForceField='@./feuilleMOR/feuille/HyperReducedFF', mappedMass='@./feuilleMOR/feuille/diamondMass' , performECSW=performECSWBool, listActiveNodesPath=listActiveNodesFile ,printLog="1")
                controlledPoints = feuille.createChild('controlledPoints')
                controlledPoints.createObject('MechanicalObject', name="actuatedPoints", template="Vec3d", position="0 0 125  0 97 45   -97 0 45   0 -97 45  97 0 45    0 0 115")

                controlledPoints.createObject('PositionEffector', template="Vec3d", indices="0", actuator="0", effectorGoal="@../../../../goal/goalMO.position")

                controlledPoints.createObject('CableActuator', template="Vec3d", name="nord" , indices="1", pullPoint="0 10 30" , maxPositiveDisp="40", minForce="0")
                controlledPoints.createObject('CableActuator', template="Vec3d", name="ouest", indices="2", pullPoint="-10 0 30", maxPositiveDisp="40", minForce="0")
                controlledPoints.createObject('CableActuator', template="Vec3d", name="sud"  , indices="3", pullPoint="0 -10 30", maxPositiveDisp="40", minForce="0")
                controlledPoints.createObject('CableActuator', template="Vec3d", name="est"  , indices="4", pullPoint="10 0 30" , maxPositiveDisp="40", minForce="0")

                controlledPoints.createObject('BarycentricMapping', mapForces="false", mapMasses="false")
                
                visuNode = feuille.createChild("visuNode")
                visuNode.createObject("OglModel",filename=path+"surface.stl", template='ExtVec3f', color='0.7 0.7 0.7 0.99',rotation="90 0 0", translation="0 0 35")
                visuNode.createObject("BarycentricMapping")
                return rootNode
                
