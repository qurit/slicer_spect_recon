import logging
import os
from typing import Annotated, Optional

import vtk

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode


#
# pytomography
#


class pyTomography(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("pytomography")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = ["Pytomography"]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Obed K. Dzikunu (QURIT), Luke Polson (QURIT), Maziar Sabouri (QURIT), Shadab Ahamed (QURIT)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#pytomography">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # pytomography1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="pytomography",
        sampleName="pytomography1",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "pytomography1.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames="pytomography1.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="pytomography1",
    )

    # pytomography2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="pytomography",
        sampleName="pytomography2",
        thumbnailFileName=os.path.join(iconsPath, "pytomography2.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames="pytomography2.nrrd",
        checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="pytomography2",
    )


#
# pytomographyParameterNode
#


@parameterNodeWrapper
class pyTomographyParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """

    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# pytomographyWidget
#


class pyTomographyWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        # self._parameterNodeGuiTag = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/pytomography.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = pyTomographyLogic()

        # Connections

        # # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).

        self.ui.PathLineEdit.connect('currentPathChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.spect_attenuation_directorybutton.connect('directoryChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.spect_collimator_combobox.connect('currentTextChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.spect_scatter_combobox.connect('currentTextChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.photopeak_combobox.connect('currentTextChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.spect_upperwindow_combobox.connect('currentTextChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.spect_lowerwindow_combobox.connect('currentTextChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.algorithm_selector_combobox.connect('currentTextChanged(QString)', self.updateParameterNodeFromGUI)
        self.ui.osem_iterations_spinbox.connect('valueChanged(int)', self.updateParameterNodeFromGUI)
        self.ui.osem_subsets_spinbox.connect('valueChanged(int)', self.updateParameterNodeFromGUI)

        # Buttons
        self.ui.PathLineEdit.connect('currentPathChanged(QString)', self.getProjectionData)
        self.ui.osem_reconstruct_pushbutton.connect('clicked(bool)', self.onReconstructButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        # if self._parameterNode:
        #     self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
        #     self._parameterNodeGuiTag = None
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)# self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        
        # if not self._parameterNode.inputVolume:
        #     firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
        #     if firstVolumeNode:
        #         self._parameterNode.inputVolume = firstVolumeNode

    # def setParameterNode(self, inputParameterNode: Optional[pytomographyParameterNode]) -> None:
    #     """
    #     Set and observe parameter node.
    #     Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    #     """

    #     if self._parameterNode:
    #         self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
    #         self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
    #     self._parameterNode = inputParameterNode
    #     if self._parameterNode:
    #         # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
    #         # ui element that needs connection.
    #         self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
    #         self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
    #         self._checkCanApply()
                
    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders


        self.ui.PathLineEdit.setCurrentPath(self._parameterNode.GetParameter("Path"))
        # self.ui.spect_attenuation_directorybutton.setDirectoryName(self._parameterNode.GetParameter("AttenuationDirectory"))
        self.ui.spect_attenuation_directorybutton.directory = self._parameterNode.GetParameter("AttenuationDirectory")
        self.ui.spect_collimator_combobox.setCurrentText(self._parameterNode.GetParameter("Collimator"))
        self.ui.spect_scatter_combobox.setCurrentText(self._parameterNode.GetParameter("Scatter"))

        photopeak_value = self._parameterNode.GetParameter("Photopeak")
        photopeak_index = self.ui.photopeak_combobox.findText(photopeak_value)
        self.ui.photopeak_combobox.setCurrentIndex(photopeak_index)

        upperwindow_value = self._parameterNode.GetParameter("UpperWindow")
        upperwindow_index = self.ui.spect_upperwindow_combobox.findText(upperwindow_value)
        self.ui.spect_upperwindow_combobox.setCurrentIndex(upperwindow_index)

        lowerwindow_value = self._parameterNode.GetParameter("LowerWindow")
        lowerwindow_index = self.ui.spect_lowerwindow_combobox.findText(lowerwindow_value)
        self.ui.spect_lowerwindow_combobox.setCurrentIndex(lowerwindow_index)

        self.ui.algorithm_selector_combobox.setCurrentText(self._parameterNode.GetParameter("Algorithm"))
        self.ui.osem_iterations_spinbox.setValue(int(self._parameterNode.GetParameter('Iterations')))
        self.ui.osem_subsets_spinbox.setValue(int(self._parameterNode.GetParameter('Subsets')))

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetParameter("Path", self.ui.PathLineEdit.currentPath)
        self._parameterNode.SetParameter("AttenuationDirectory", self.ui.spect_attenuation_directorybutton.directory)
        self._parameterNode.SetParameter("Collimator", self.ui.spect_collimator_combobox.currentText)
        self._parameterNode.SetParameter("Scatter", self.ui.spect_scatter_combobox.currentText)
        self._parameterNode.SetParameter("Photopeak", str(self.ui.photopeak_combobox.currentText))
        self._parameterNode.SetParameter("UpperWindow", str(self.ui.spect_upperwindow_combobox.currentText))
        self._parameterNode.SetParameter("LowerWindow", str(self.ui.spect_lowerwindow_combobox.currentText))
        self._parameterNode.SetParameter("Algorithm", self.ui.algorithm_selector_combobox.currentText)
        self._parameterNode.SetParameter("Iterations", str(self.ui.osem_iterations_spinbox.value))
        self._parameterNode.SetParameter("Subsets", str(self.ui.osem_subsets_spinbox.value))

        self._parameterNode.EndModify(wasModified)


    def getProjectionData(self, directory):
        energy_window = self.logic.getEnergyWindow(directory)
        self.ui.spect_upperwindow_combobox.addItems(energy_window)
        # self.ui.spect_scatter_combobox.currentTextChanged.connect(self.logic.energyWindowType)
        self.ui.spect_lowerwindow_combobox.addItems(energy_window)
        self.ui.photopeak_combobox.addItems(energy_window)



    # def _checkCanApply(self, caller=None, event=None) -> None:
    #     if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
    #         self.ui.applyButton.toolTip = _("Compute output volume")
    #         self.ui.applyButton.enabled = True
    #     else:
    #         self.ui.applyButton.toolTip = _("Select input and output volume nodes")
    #         self.ui.applyButton.enabled = False
        
    def onReconstructButton(self):
        path= self.logic.reconstruct( 
            self.ui.PathLineEdit.currentPath, self.ui.spect_attenuation_directorybutton.directory, 
            self.ui.spect_collimator_combobox.currentText, self.ui.spect_scatter_combobox.currentText, 
            self.ui.photopeak_combobox.currentIndex, self.ui.spect_upperwindow_combobox.currentIndex, 
            self.ui.spect_lowerwindow_combobox.currentIndex, self.ui.algorithm_selector_combobox.currentText, 
            self.ui.osem_iterations_spinbox.value, self.ui.osem_subsets_spinbox.value
        )
        self.logic.process(path)

    # def onApplyButton(self) -> None:
    #     """Run processing when user clicks "Apply" button."""
    #     with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
    #         # Compute output
    #         self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
    #                            self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)

    #         # Compute inverted output (if needed)
    #         if self.ui.invertedOutputSelector.currentNode():
    #             # If additional output volume is selected then result with inverted threshold is written there
    #             self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
    #                                self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)


#
# pytomographyLogic
#



class pyTomographyLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """


    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        slicer.util.pip_install("pytomography==2.0.1")
        print("Im here")

    
    def getEnergyWindow(self, directory):

        import pydicom
        ds = pydicom.read_file(directory)

        energy_windows =[]
        lower_limits = []
        for energy_window_information in ds.EnergyWindowInformationSequence:
            lower_limit = energy_window_information.EnergyWindowRangeSequence[0].EnergyWindowLowerLimit
            upper_limit = energy_window_information.EnergyWindowRangeSequence[0].EnergyWindowUpperLimit
            energy_window_name = energy_window_information.EnergyWindowName
            lower_limits.append(lower_limit)
            energy_windows.append(f'{energy_window_name} ({lower_limit}keV - {upper_limit}keV)')

        import numpy as np
        energy_windows = list(np.array(energy_windows)[np.argsort(lower_limits)])

        return energy_windows

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        # if not parameterNode.GetParameter("Path"):
        #     parameterNode.SetParameter("Path", "Select projection data")
        # if not parameterNode.GetParameter("AttenuationDirectory"):
        #     parameterNode.SetParameter("AttenuationDirectory", "Select CT files folder")
        if not parameterNode.GetParameter("Collimator"):
            parameterNode.SetParameter("Collimator", "Choose Collimator")
        if not parameterNode.GetParameter("Scatter"):
            parameterNode.SetParameter("Scatter", "Select Scatter Window")
        if not parameterNode.GetParameter("UpperWindow"):
            parameterNode.SetParameter("UpperWindow", "Select Upper Window")
        if not parameterNode.GetParameter("LowerWindow"):
            parameterNode.SetParameter("LowerWindow", "Select Lower Window")
        if not parameterNode.GetParameter("Algorithm"):
            parameterNode.SetParameter("Algorithm", "Select Algorithm")
        if not parameterNode.GetParameter("Iterations"):
            parameterNode.SetParameter("Iterations", "0")
        if not parameterNode.GetParameter("Subsets"):
            parameterNode.SetParameter("Subsets", "0")

    def reconstruct(self, projection_data, ct_path, collimator, scatter, photopeak, upperwindow, lowerwindow, algorithm, iter, subset):
        import pytomography    
        from pytomography.utils import print_collimator_parameters

        print("Reconstructing volume...")

        import os
        files_CT = [os.path.join(ct_path, file) for file in os.listdir(ct_path)]
        
        from pytomography.io.SPECT import dicom
        self.object_meta, self.proj_meta = dicom.get_metadata(projection_data)
        self.projections = dicom.get_projections(projection_data, photopeak)
        scatter = dicom.get_scatter_from_TEW(projection_data, photopeak, lowerwindow, upperwindow)

        from pytomography.transforms.SPECT import SPECTAttenuationTransform, SPECTPSFTransform
        att_transform = SPECTAttenuationTransform(filepath=files_CT)
        att_transform.configure(self.object_meta, self.proj_meta)
        collimator_name = collimator
        #TODO dynamically select energy
        energy_kev = 208
        psf_meta = dicom.get_psfmeta_from_scanner_params(collimator_name, energy_kev)
        psf_transform = SPECTPSFTransform(psf_meta)
        
        from pytomography.projectors.SPECT import SPECTSystemMatrix
        system_matrix = SPECTSystemMatrix(
        obj2obj_transforms = [att_transform,psf_transform],
        proj2proj_transforms = [],
        object_meta = self.object_meta,
        proj_meta = self.proj_meta)

        from pytomography.likelihoods import PoissonLogLikelihood
        likelihood = PoissonLogLikelihood(system_matrix, self.projections, scatter)

        from pytomography.algorithms import OSEM
        if algorithm == "OSEM":
            reconstruction_algorithm = OSEM(likelihood)
        
        reconstructed_object = reconstruction_algorithm(n_iters=iter, n_subsets=subset)

        save_path = r"C:\Users\okdzi\OneDrive\Desktop\projectiondata\newfolder"
        dicom.save_dcm(save_path, reconstructed_object, projection_data, "tryosem")
        print("Reconstruction successful")

        return save_path



    # def getParameterNode(self):
    #     return pyTomographyParameterNode(super().getParameterNode())

    def process(self, reconstructed_volume_directory):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        # Create a DICOM reader
        reader = vtk.vtkDICOMImageReader()
        # Set the directory containing the DICOM files
        reader.SetDirectoryName(reconstructed_volume_directory)
        # Update the reader
        reader.Update()

        # Get the output of the reader, which is the VTK image data representing the reconstructed volume
        reconstructed_volume_vtk = reader.GetOutput()

        # Create a new Slicer volume node
        reconstructed_volume_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        reconstructed_volume_node.SetName("ReconstructedVolume")  # Set a name for the volume node

        # Set the VTK image data to the volume node
        reconstructed_volume_node.SetAndObserveImageData(reconstructed_volume_vtk)

        volumeNode = slicer.util.getNode("ReconstructedVolume")
        displayNode = volumeNode.GetDisplayNode()
        displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
        slicer.mrmlScene.AddNode(displayNode)
        volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.SetAutoWindowLevel(True)
        # displayNode.SetWindow(50)
        # displayNode.SetLevel(100)

        displayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeGrey")

        zoomLevel = 1.0 / max(volumeNode.GetImageData().GetDimensions())

        layoutManager = slicer.app.layoutManager()
        for sliceViewName in layoutManager.sliceViewNames():
            layoutManager.sliceWidget(sliceViewName).mrmlSliceNode().RotateToVolumePlane(volumeNode)
            layoutManager.sliceWidget(sliceViewName).sliceLogic().GetSliceCompositeNode().SetForegroundVolumeID(volumeNode.GetID())
            layoutManager.sliceWidget(sliceViewName).sliceController().fitSliceToBackground()

            layoutManager.sliceWidget(sliceViewName).sliceLogic().GetSliceCompositeNode().SetAttribute("scale factor", str(0.01))

    
            


        # for color in ["Red", "Yellow", "Green"]:
        #     slicer.app.layoutManager().sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetForegroundVolumeID(volumeNode.GetID())
        


        # Get the volume node
        # volumeNode = slicer.util.getNode("ReconstructedVolume")

        # # Set the volume node as the background for slice viewer layers
        # slicer.util.setSliceViewerLayers(background=volumeNode)

        # volumeNode = slicer.util.getNode("ReconstructedVolume")
        # applicationLogic = slicer.app.applicationLogic()
        # selectionNode = applicationLogic.GetSelectionNode()
        # selectionNode.SetSecondaryVolumeID(volumeNode.GetID())
        # applicationLogic.PropagateForegroundVolumeSelection(0)




        # n =  slicer.util.getNode("ReconstructedVolume")
        # # displayNode = n.GetDisplayNode()
        # # displayNode.SetAutoWindowLevel(True)

        # if n:
        # # Get the display node of the volume node
        #     displayNode = n.GetDisplayNode()

        #     if displayNode is None:
        #         # If no display node exists, create one
        #         displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
        #         slicer.mrmlScene.AddNode(displayNode)
        #         n.SetAndObserveDisplayNodeID(displayNode.GetID())
            
        #     # Enable auto window/level
        #     displayNode.SetAutoWindowLevel(True)

        # else:
        #     print("Volume node not found")

        # for color in ["Red", "Yellow", "Green"]:
        #     slicer.app.layoutManager().sliceWidget(color).sliceLogic().GetSliceCompositeNode().SetForegroundVolumeID(n.GetID())


        # # Get the volume node
        # volumeNode = slicer.util.getNode("ReconstructedVolume")
        # if volumeNode:
        #     # Check if the volume node has an associated display node
        #     displayNode = volumeNode.GetDisplayNode()
        #     if displayNode is None:
        #         # If no display node exists, create one
        #         displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
        #         slicer.mrmlScene.AddNode(displayNode)
        #         volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())
        #     else:
        #         print("Volume node already has a display node")

        #     # Enable auto window/level
        #     if displayNode:
        #         displayNode.SetAutoWindowLevel(True)
        #         print("Auto window/level enabled")
        #     else:
        #         print("Failed to set auto window/level: Display node is None")

        #     # Set the color node reference to a built-in color table
        #     displayNode.SetDefaultColorMap()
        #     print("Color map set to default")

        #     for color in ["Red", "Yellow", "Green"]:
        #         sliceWidget = slicer.app.layoutManager().sliceWidget(color)
        #         if sliceWidget:
        #             sliceLogic = sliceWidget.sliceLogic()
        #             compositeNode = sliceLogic.GetSliceCompositeNode()
        #             if compositeNode:
        #                 compositeNode.SetForegroundVolumeID(volumeNode.GetID())
        #                 print(f"Foreground volume set for {color} slice view")
        #             else:
        #                 print(f"Failed to set foreground volume for {color} slice view: Composite node is None")
        #         else:
        #             print(f"Failed to get slice widget for {color} slice view")
        # else:
        #     print("Volume node not found")




        # if not inputVolume or not outputVolume:
        #     raise ValueError("Input or output volume is invalid")

        # import time

        # startTime = time.time()
        # logging.info("Processing started")

        # # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        # cliParams = {
        #     "InputVolume": inputVolume.GetID(),
        #     "OutputVolume": outputVolume.GetID(),
        #     "ThresholdValue": imageThreshold,
        #     "ThresholdType": "Above" if invert else "Below",
        # }
        # cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        # slicer.mrmlScene.RemoveNode(cliNode)

        # stopTime = time.time()
        # logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")


    def install_required_packages(self):
        
        try: 
            # Install pytomography
            slicer.util.pip_install("pytomography==2.0.1")
            print("Packages installed successfully!")

        except Exception as e:
            print(f"Error installing packages: {e}")




#
# pytomographyTest
#


class pyTomographyTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_pytomography1()

    def test_pytomography1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData

        registerSampleData()
        inputVolume = SampleData.downloadSample("pytomography1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = pyTomographyLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay("Test passed")
