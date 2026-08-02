"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_models_union.py.tmpl
Derived from: src/mmdio/engine/registry.ttl + packs/mmdio-pack/ontology.ttl
"""

from mmdio.engine.types.block_models import BlockDiagram
from mmdio.engine.models import C4Diagram
from mmdio.engine.models import ClassDiagram
from mmdio.engine.models import ERDiagram
from mmdio.engine.models import FlowchartDiagram
from mmdio.engine.models import GanttChart
from mmdio.engine.models import GitGraph
from mmdio.engine.types.kanban_models import KanbanDiagram
from mmdio.engine.models import Mindmap
from mmdio.engine.models import PieChart
from mmdio.engine.models import SankeyDiagram
from mmdio.engine.models import SequenceDiagram
from mmdio.engine.models import StateDiagram
from mmdio.engine.types.timeline_models import TimelineDiagram
from mmdio.engine.types.xychart_models import XYChartDiagram

MermaidDiagram = (
    BlockDiagram |

    C4Diagram |

    ClassDiagram |

    ERDiagram |

    FlowchartDiagram |

    GanttChart |

    GitGraph |

    KanbanDiagram |

    Mindmap |

    PieChart |

    SankeyDiagram |

    SequenceDiagram |

    StateDiagram |

    TimelineDiagram |

    XYChartDiagram


)
"""Union type for all supported Mermaid diagram types. Use with Pydantic discriminated unions."""
