"""Module for the integrator class."""

from enum import Enum

from lammpsinputbuilder.group import Group, AllGroup
from lammpsinputbuilder.types import GlobalInformation


class Integrator:
    """Base class for all integrators."""

    def __init__(self, integrator_name: str = "defaultIntegrator") -> None:
        self.integrator_name = integrator_name

    def getIntegratorName(self) -> str:
        return self.integrator_name

    def to_dict(self) -> dict:
        result = {}
        result["class"] = self.__class__.__name__
        result["integrator_name"] = self.integrator_name
        return result

    def from_dict(self, d: dict, version: int):
        self.integrator_name = d.get("integrator_name", "defaultIntegrator")

    def add_do_commands(self, global_information: GlobalInformation) -> str:
        return ""

    def add_undo_commands(self) -> str:
        return ""

    def addRunCommands(self) -> str:
        return ""


class RunZeroIntegrator(Integrator):
    def __init__(self, integrator_name: str = "RunZero") -> None:
        super().__init__(integrator_name=integrator_name)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["class"] = self.__class__.__name__
        return result

    def from_dict(self, d: dict, version: int):
        if d["class"] != self.__class__.__name__:
            raise ValueError(
                f"Expected class {self.__class__.__name__}, got {d['class']}.")
        super().from_dict(d, version=version)

    def addRunCommands(self) -> str:
        return "run 0\n"


class NVEIntegrator(Integrator):
    def __init__(
            self,
            integrator_name: str = "NVEID",
            group: Group = AllGroup(),
            nbSteps: int = 5000) -> None:
        super().__init__(integrator_name=integrator_name)
        self.group = group.get_group_name()
        self.nbSteps = nbSteps

    def get_group_name(self) -> str:
        return self.group

    def getNbSteps(self) -> int:
        return self.nbSteps

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["class"] = self.__class__.__name__
        result["group_name"] = self.group
        result["nbSteps"] = self.nbSteps
        return result

    def from_dict(self, d: dict, version: int):
        if d["class"] != self.__class__.__name__:
            raise ValueError(
                f"Expected class {self.__class__.__name__}, got {d['class']}.")
        super().from_dict(d, version=version)
        self.group = d["group_name"]
        self.nbSteps = d.get("nbSteps", 5000)

    def add_do_commands(self, global_information: GlobalInformation) -> str:
        return f"fix {self.integrator_name} {self.group} nve\n"

    def add_undo_commands(self) -> str:
        return f"unfix {self.integrator_name}\n"

    def addRunCommands(self) -> str:
        return f"run {self.nbSteps}\n"


class MinimizeStyle(Enum):
    CG = 0,
    SD = 1,
    SPIN_LBFGS = 2


class MinimizeIntegrator(Integrator):

    minimizeStyleToStr = {
        MinimizeStyle.CG: "cg",
        MinimizeStyle.SD: "sd",
        MinimizeStyle.SPIN_LBFGS: "spin/lbfgs"
    }

    def __init__(
            self,
            integrator_name: str = "Minimize",
            style: MinimizeStyle = MinimizeStyle.CG,
            etol: float = 0.01,
            ftol: float = 0.01,
            maxiter: int = 100,
            maxeval: int = 10000) -> None:
        super().__init__(integrator_name=integrator_name)
        self.style = style
        self.etol = etol
        self.ftol = ftol
        self.maxiter = maxiter
        self.maxeval = maxeval

    def getStyle(self) -> MinimizeStyle:
        return self.style

    def getEtol(self) -> float:
        return self.etol

    def getFtol(self) -> float:
        return self.ftol

    def getMaxiter(self) -> int:
        return self.maxiter

    def getMaxeval(self) -> int:
        return self.maxeval

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["class"] = self.__class__.__name__
        result["style"] = self.style.value
        result["etol"] = self.etol
        result["ftol"] = self.ftol
        result["maxiter"] = self.maxiter
        result["maxeval"] = self.maxeval
        return result

    def from_dict(self, d: dict, version: int):
        if d["class"] != self.__class__.__name__:
            raise ValueError(
                f"Expected class {self.__class__.__name__}, got {d['class']}.")
        super().from_dict(d, version)
        self.style = MinimizeStyle(d["style"])
        self.etol = d["etol"]
        self.ftol = d["ftol"]
        self.maxiter = d["maxiter"]
        self.maxeval = d["maxeval"]

    def add_do_commands(self, global_information: GlobalInformation) -> str:
        return ""

    def add_undo_commands(self) -> str:
        return ""

    def addRunCommands(self) -> str:
        result = f"min_style {MinimizeIntegrator.minimizeStyleToStr[self.style]}\n"
        result += f"minimize {self.etol} {self.ftol} {self.maxiter} {self.maxeval}\n"
        return result

    def getMinimizeStyle(self) -> MinimizeStyle:
        return self.style


class MultipassMinimizeIntegrator(Integrator):

    def __init__(self, integrator_name: str = "MultiMinimize") -> None:
        super().__init__(integrator_name=integrator_name)

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["class"] = self.__class__.__name__
        return result

    def from_dict(self, d: dict, version: int):
        if d["class"] != self.__class__.__name__:
            raise ValueError(
                f"Expected class {self.__class__.__name__}, got {d['class']}.")
        super().from_dict(d, version)

    def add_do_commands(self, global_information: GlobalInformation) -> str:
        return ""

    def add_undo_commands(self) -> str:
        return ""

    def addRunCommands(self) -> str:
        commands = ""
        commands += "min_style      cg\n"
        commands += "minimize       1.0e-10 1.0e-10 10000 100000\n"

        commands += "min_style      hftn\n"
        commands += "minimize       1.0e-10 1.0e-10 10000 100000\n"

        commands += 'min_style      sd\n'
        commands += 'minimize       1.0e-10 1.0e-10 10000 100000\n'

        commands += 'variable       i loop 100\n'
        commands += 'label          loop1\n'
        commands += 'variable       ene_min equal pe\n'
        commands += 'variable       ene_min_i equal ${ene_min}\n'

        commands += 'min_style      cg\n'
        commands += 'minimize       1.0e-10 1.0e-10 10000 100000\n'

        commands += 'min_style      hftn\n'
        commands += 'minimize       1.0e-10 1.0e-10 10000 100000\n'

        commands += 'min_style      sd\n'
        commands += 'minimize       1.0e-10 1.0e-10 10000 100000\n'

        commands += 'variable       ene_min_f equal pe\n'
        commands += 'variable       ene_diff equal ${ene_min_i}-${ene_min_f}\n'
        commands += 'print          "Delta_E = ${ene_diff}"\n'
        commands += 'if             "${ene_diff}<1e-6" then "jump SELF break1"\n'
        commands += 'print          "Loop_id = $i"\n'
        commands += 'next           i\n'
        commands += 'jump           SELF loop1\n'
        commands += 'label          break1\n'
        commands += 'variable       i delete\n'
        return commands


class ManualIntegrator(Integrator):

    def __init__(
            self,
            integrator_name: str = "Manual",
            cmdDo: str = "",
            cmdUndo: str = "",
            cmdRun: str = "") -> None:
        super().__init__(integrator_name=integrator_name)
        self.cmdDo = cmdDo
        self.cmdUndo = cmdUndo
        self.cmdRun = cmdRun

    def getDoCommands(self) -> str:
        return self.cmdDo

    def getUndoCommands(self) -> str:
        return self.cmdUndo

    def getRunCommands(self) -> str:
        return self.cmdRun

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["class"] = self.__class__.__name__
        result["cmdDo"] = self.cmdDo
        result["cmdUndo"] = self.cmdUndo
        result["cmdRun"] = self.cmdRun
        return result

    def from_dict(self, d: dict, version: int):
        if d["class"] != self.__class__.__name__:
            raise ValueError(
                f"Expected class {self.__class__.__name__}, got {d['class']}.")
        super().from_dict(d, version)
        self.cmdDo = d["cmdDo"]
        self.cmdUndo = d["cmdUndo"]
        self.cmdRun = d["cmdRun"]

    def add_do_commands(self, global_information: GlobalInformation) -> str:
        if self.cmdDo.endswith("\n"):
            return self.cmdDo
        else:
            return self.cmdDo + "\n"

    def add_undo_commands(self) -> str:
        if self.cmdUndo.endswith("\n"):
            return self.cmdUndo
        else:
            return self.cmdUndo + "\n"

    def addRunCommands(self) -> str:
        if self.cmdRun.endswith("\n"):
            return self.cmdRun
        else:
            return self.cmdRun + "\n"
