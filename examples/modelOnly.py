#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import logging

from lammpsinputbuilder.types import BoundingBoxStyle, ElectrostaticMethod
from lammpsinputbuilder.typedMolecule import ReaxTypedMolecularSystem
from lammpsinputbuilder.workflowBuilder import WorkflowBuilder

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler())


def main():
    modelData = Path(__file__).parent.parent / \
        'data' / 'models' / 'benzene.xyz'
    forcefield = Path(__file__).parent.parent / 'data' / \
        'potentials' / 'ffield.reax.Fe_O_C_H.reax'

    typedMolecule = ReaxTypedMolecularSystem(
        bboxStyle=BoundingBoxStyle.PERIODIC,
        electrostaticMethod=ElectrostaticMethod.QEQ
    )
    typedMolecule.loadFromFile(modelData, forcefield)

    # Create the workflow. In this case, it's only the molecule
    workflow = WorkflowBuilder()
    workflow.set_typed_molecular_system(typedMolecule)

    # Generate the inputs
    job_folder = workflow.generate_inputs()

    logger.info(f"Inputs generated in the job folder: {job_folder}")


if __name__ == "__main__":
    main()
