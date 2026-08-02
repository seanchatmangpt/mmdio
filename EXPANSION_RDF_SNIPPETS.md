# Complete RDF Snippets: Hand-Written Types (Tier 1 Migration)

This document provides the exact RDF triples to add to `packs/mmdio-pack/ontology.ttl` for the 10 hand-written diagram types. Each snippet is copy-paste ready.

---

## Prerequisites

Before pasting any snippets below:

1. Ensure all enums are defined (see the enum section at end of this file)
2. Run `ggen sync run` after each batch to validate
3. Verify gates pass: `ggen gate validate packs/mmdio-pack/gates/`

---

## 2.1 Type: stateDiagram (pythonInternalId: "state")

**Source Models:**
- `src/mmdio/engine/models.py`: StateDiagram, StateNode, StateTransition
- `src/mmdio/engine/parser.py`: StateTransformer
- `src/mmdio/engine/render.py`: render_state
- `src/mmdio/engine/grammars/state.lark`

**RDF Triples:**

```ttl
mer:Type_stateDiagram
  mer:pythonSupport true ;
  mer:pythonInternalId "state" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "StateDiagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "StateTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_state" ;
  mer:grammarFile "state.lark" ;
  mer:detectPattern "^\\s*statediagram(-v2)?\\b" ;
  mer:hasModel mer:Model_StateDiagram, mer:Model_StateNode, mer:Model_StateTransition .

mer:Model_StateDiagram a mer:PythonModel ;
  mer:className "StateDiagram" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "stateDiagram-v2" ;
  mer:field mer:Field_StateDiagram_initial_state, 
            mer:Field_StateDiagram_states,
            mer:Field_StateDiagram_transitions .

mer:Field_StateDiagram_initial_state a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "initial_state" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Initial state identifier" ;
  mer:fieldExampleValue "[*]" .

mer:Field_StateDiagram_states a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "states" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "StateNode" ;
  mer:fieldDescription "List of states" ;
  mer:fieldRenderFormat "  {_r1.id}" ;
  mer:fieldExampleValue "" .

mer:Field_StateDiagram_transitions a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "transitions" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "StateTransition" ;
  mer:fieldDescription "List of transitions between states" ;
  mer:fieldRenderFormat "  {_r1.source} --> {_r1.target} : {_r1.label}" ;
  mer:fieldExampleValue "" .

mer:Model_StateNode a mer:PythonModel ;
  mer:className "StateNode" ;
  mer:isTopLevel false ;
  mer:field mer:Field_StateNode_id, mer:Field_StateNode_label .

mer:Field_StateNode_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "State identifier" ;
  mer:fieldExampleValue "state_1" .

mer:Field_StateNode_label a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "State display label" ;
  mer:fieldExampleValue "Active" .

mer:Model_StateTransition a mer:PythonModel ;
  mer:className "StateTransition" ;
  mer:isTopLevel false ;
  mer:field mer:Field_StateTransition_source,
            mer:Field_StateTransition_target,
            mer:Field_StateTransition_label .

mer:Field_StateTransition_source a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "source" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Source state ID" ;
  mer:fieldExampleValue "state_1" .

mer:Field_StateTransition_target a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "target" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Target state ID" ;
  mer:fieldExampleValue "state_2" .

mer:Field_StateTransition_label a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Transition label/trigger" ;
  mer:fieldExampleValue "event" .
```

---

## 2.2 Type: erDiagram (pythonInternalId: "er")

**RDF Triples:**

```ttl
mer:Type_er
  mer:pythonSupport true ;
  mer:pythonInternalId "er" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "ERDiagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "ERTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_er" ;
  mer:grammarFile "er.lark" ;
  mer:detectPattern "^\\s*erdiagram\\b" ;
  mer:hasModel mer:Model_ERDiagram, mer:Model_EREntity, mer:Model_ERAttribute, mer:Model_ERRelationship .

mer:Model_ERDiagram a mer:PythonModel ;
  mer:className "ERDiagram" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "erDiagram" ;
  mer:field mer:Field_ERDiagram_entities, mer:Field_ERDiagram_relationships .

mer:Field_ERDiagram_entities a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "entities" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "EREntity" ;
  mer:fieldDescription "List of entities" ;
  mer:fieldRenderFormat "  {_r1.name} \"\"" ;
  mer:fieldExampleValue "" .

mer:Field_ERDiagram_relationships a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "relationships" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "ERRelationship" ;
  mer:fieldDescription "List of entity relationships" ;
  mer:fieldRenderFormat "  {_r1.entity_a} {_r1.cardinality_a} --> {_r1.cardinality_b} {_r1.entity_b} : {_r1.relation_type}" ;
  mer:fieldExampleValue "" .

mer:Model_EREntity a mer:PythonModel ;
  mer:className "EREntity" ;
  mer:isTopLevel false ;
  mer:field mer:Field_EREntity_name, mer:Field_EREntity_attributes .

mer:Field_EREntity_name a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "name" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Entity name" ;
  mer:fieldExampleValue "USER" .

mer:Field_EREntity_attributes a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "attributes" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "ERAttribute" ;
  mer:fieldDescription "Entity attributes" ;
  mer:fieldRenderFormat "    {_r2.name} {_r2.attr_type}" ;
  mer:fieldExampleValue "" .

mer:Model_ERAttribute a mer:PythonModel ;
  mer:className "ERAttribute" ;
  mer:isTopLevel false ;
  mer:field mer:Field_ERAttribute_name, mer:Field_ERAttribute_attr_type .

mer:Field_ERAttribute_name a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "name" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Attribute name" ;
  mer:fieldExampleValue "id" .

mer:Field_ERAttribute_attr_type a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "attr_type" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Attribute type (int, string, etc.)" ;
  mer:fieldExampleValue "int" .

mer:Model_ERRelationship a mer:PythonModel ;
  mer:className "ERRelationship" ;
  mer:isTopLevel false ;
  mer:field mer:Field_ERRelationship_entity_a,
            mer:Field_ERRelationship_entity_b,
            mer:Field_ERRelationship_cardinality_a,
            mer:Field_ERRelationship_cardinality_b,
            mer:Field_ERRelationship_relation_type .

mer:Field_ERRelationship_entity_a a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "entity_a" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "First entity name" ;
  mer:fieldExampleValue "USER" .

mer:Field_ERRelationship_entity_b a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "entity_b" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Second entity name" ;
  mer:fieldExampleValue "ORDER" .

mer:Field_ERRelationship_cardinality_a a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "cardinality_a" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Cardinality of entity_a side" ;
  mer:fieldExampleValue "|o" .

mer:Field_ERRelationship_cardinality_b a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "cardinality_b" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Cardinality of entity_b side" ;
  mer:fieldExampleValue "o|" .

mer:Field_ERRelationship_relation_type a mer:PythonField ;
  mer:fieldOrder 5 ;
  mer:fieldName "relation_type" ;
  mer:fieldKind "enum" ;
  mer:fieldPyType "RelationshipType" ;
  mer:fieldDescription "Type of relationship" ;
  mer:fieldExampleValue "ASSOCIATION" .
```

---

## 2.3 Type: ganttChart (pythonInternalId: "gantt")

```ttl
mer:Type_gantt
  mer:pythonSupport true ;
  mer:pythonInternalId "gantt" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "GanttChart" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "GanttTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_gantt" ;
  mer:grammarFile "gantt.lark" ;
  mer:detectPattern "^\\s*gantt\\b" ;
  mer:hasModel mer:Model_GanttChart, mer:Model_GanttTask, mer:Model_GanttDependency .

mer:Model_GanttChart a mer:PythonModel ;
  mer:className "GanttChart" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "gantt" ;
  mer:field mer:Field_GanttChart_title,
            mer:Field_GanttChart_date_format,
            mer:Field_GanttChart_tasks .

mer:Field_GanttChart_title a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "title" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Chart title" ;
  mer:fieldExampleValue "Project Timeline" .

mer:Field_GanttChart_date_format a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "date_format" ;
  mer:fieldKind "literal-default" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Date format (YYYY-MM-DD, etc.)" ;
  mer:fieldDefault "\"YYYY-MM-DD\"" ;
  mer:fieldExampleValue "YYYY-MM-DD" .

mer:Field_GanttChart_tasks a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "tasks" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "GanttTask" ;
  mer:fieldDescription "List of tasks" ;
  mer:fieldRenderFormat "  {_r1.id} : {_r1.status} , {_r1.start_date}, {_r1.end_date}" ;
  mer:fieldExampleValue "" .

mer:Model_GanttTask a mer:PythonModel ;
  mer:className "GanttTask" ;
  mer:isTopLevel false ;
  mer:field mer:Field_GanttTask_id,
            mer:Field_GanttTask_title,
            mer:Field_GanttTask_status,
            mer:Field_GanttTask_start_date,
            mer:Field_GanttTask_end_date,
            mer:Field_GanttTask_dependencies .

mer:Field_GanttTask_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Task identifier" ;
  mer:fieldExampleValue "task1" .

mer:Field_GanttTask_title a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "title" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Task title/name" ;
  mer:fieldExampleValue "Phase 1" .

mer:Field_GanttTask_status a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "status" ;
  mer:fieldKind "enum" ;
  mer:fieldPyType "TaskStatus" ;
  mer:fieldDescription "Task status (active, done, milestone, crit, etc.)" ;
  mer:fieldExampleValue "ACTIVE" .

mer:Field_GanttTask_start_date a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "start_date" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Task start date" ;
  mer:fieldExampleValue "2024-01-01" .

mer:Field_GanttTask_end_date a mer:PythonField ;
  mer:fieldOrder 5 ;
  mer:fieldName "end_date" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Task end date" ;
  mer:fieldExampleValue "2024-01-31" .

mer:Field_GanttTask_dependencies a mer:PythonField ;
  mer:fieldOrder 6 ;
  mer:fieldName "dependencies" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "GanttDependency" ;
  mer:fieldDescription "Task dependencies" ;
  mer:fieldRenderFormat "  " ;
  mer:fieldExampleValue "" .

mer:Model_GanttDependency a mer:PythonModel ;
  mer:className "GanttDependency" ;
  mer:isTopLevel false ;
  mer:field mer:Field_GanttDependency_task_id .

mer:Field_GanttDependency_task_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "task_id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "ID of dependent task" ;
  mer:fieldExampleValue "task0" .
```

---

## 2.4 Type: gitGraph (pythonInternalId: "git")

```ttl
mer:Type_gitGraph
  mer:pythonSupport true ;
  mer:pythonInternalId "git" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "GitGraph" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "GitTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_git" ;
  mer:grammarFile "git.lark" ;
  mer:detectPattern "^\\s*gitgraph\\b" ;
  mer:hasModel mer:Model_GitGraph, mer:Model_GitCommit, mer:Model_GitBranch .

mer:Model_GitGraph a mer:PythonModel ;
  mer:className "GitGraph" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "gitGraph" ;
  mer:field mer:Field_GitGraph_main_branch, mer:Field_GitGraph_commits .

mer:Field_GitGraph_main_branch a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "main_branch" ;
  mer:fieldKind "literal-default" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Main branch name" ;
  mer:fieldDefault "\"main\"" ;
  mer:fieldExampleValue "main" .

mer:Field_GitGraph_commits a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "commits" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "GitCommit" ;
  mer:fieldDescription "List of commits" ;
  mer:fieldRenderFormat "  commit id: \"{_r1.id}\"" ;
  mer:fieldExampleValue "" .

mer:Model_GitCommit a mer:PythonModel ;
  mer:className "GitCommit" ;
  mer:isTopLevel false ;
  mer:field mer:Field_GitCommit_id, mer:Field_GitCommit_message .

mer:Field_GitCommit_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Commit identifier (hash)" ;
  mer:fieldExampleValue "abc1234" .

mer:Field_GitCommit_message a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "message" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Commit message" ;
  mer:fieldExampleValue "Initial commit" .

mer:Model_GitBranch a mer:PythonModel ;
  mer:className "GitBranch" ;
  mer:isTopLevel false ;
  mer:field mer:Field_GitBranch_name .

mer:Field_GitBranch_name a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "name" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Branch name" ;
  mer:fieldExampleValue "feature/x" .
```

---

## 2.5 Type: c4Diagram (pythonInternalId: "c4")

```ttl
mer:Type_c4
  mer:pythonSupport true ;
  mer:pythonInternalId "c4" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "C4Diagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "C4Transformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_c4" ;
  mer:grammarFile "c4.lark" ;
  mer:detectPattern "^\\s*c4(context|diagram)\\b" ;
  mer:hasModel mer:Model_C4Diagram, mer:Model_C4Element, mer:Model_C4Relationship .

mer:Model_C4Diagram a mer:PythonModel ;
  mer:className "C4Diagram" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "C4Context" ;
  mer:field mer:Field_C4Diagram_title, 
            mer:Field_C4Diagram_level,
            mer:Field_C4Diagram_elements,
            mer:Field_C4Diagram_relationships .

mer:Field_C4Diagram_title a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "title" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Diagram title" ;
  mer:fieldExampleValue "System Context" .

mer:Field_C4Diagram_level a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "level" ;
  mer:fieldKind "enum" ;
  mer:fieldPyType "C4Level" ;
  mer:fieldDescription "C4 level (C1, C2, C3, C4)" ;
  mer:fieldExampleValue "C1" .

mer:Field_C4Diagram_elements a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "elements" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "C4Element" ;
  mer:fieldDescription "Systems, containers, or components" ;
  mer:fieldRenderFormat "  {_r1.type}({_r1.id}, \"{_r1.name}\", \"{_r1.description}\")" ;
  mer:fieldExampleValue "" .

mer:Field_C4Diagram_relationships a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "relationships" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "C4Relationship" ;
  mer:fieldDescription "Relationships between elements" ;
  mer:fieldRenderFormat "  Rel({_r1.source}, {_r1.target}, \"{_r1.label}\")" ;
  mer:fieldExampleValue "" .

mer:Model_C4Element a mer:PythonModel ;
  mer:className "C4Element" ;
  mer:isTopLevel false ;
  mer:field mer:Field_C4Element_id,
            mer:Field_C4Element_name,
            mer:Field_C4Element_description,
            mer:Field_C4Element_type .

mer:Field_C4Element_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Element identifier" ;
  mer:fieldExampleValue "user" .

mer:Field_C4Element_name a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "name" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Element name" ;
  mer:fieldExampleValue "User" .

mer:Field_C4Element_description a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "description" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Element description" ;
  mer:fieldExampleValue "A user of the system" .

mer:Field_C4Element_type a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "type" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Element type (System, Person, Container, etc.)" ;
  mer:fieldExampleValue "Person" .

mer:Model_C4Relationship a mer:PythonModel ;
  mer:className "C4Relationship" ;
  mer:isTopLevel false ;
  mer:field mer:Field_C4Relationship_source,
            mer:Field_C4Relationship_target,
            mer:Field_C4Relationship_label .

mer:Field_C4Relationship_source a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "source" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Source element ID" ;
  mer:fieldExampleValue "user" .

mer:Field_C4Relationship_target a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "target" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Target element ID" ;
  mer:fieldExampleValue "system" .

mer:Field_C4Relationship_label a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Relationship description" ;
  mer:fieldExampleValue "uses" .
```

---

## 2.6 Type: xychart (pythonInternalId: "xychart")

```ttl
mer:Type_xychart
  mer:pythonSupport true ;
  mer:pythonInternalId "xychart" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "XYChartDiagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "XYChartTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_xychart" ;
  mer:grammarFile "xychart.lark" ;
  mer:detectPattern "^\\s*xychart(-beta)?\\b" ;
  mer:hasModel mer:Model_XYChartDiagram, mer:Model_XYAxis, mer:Model_DataSeries .

mer:Model_XYChartDiagram a mer:PythonModel ;
  mer:className "XYChartDiagram" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "xychart-beta" ;
  mer:field mer:Field_XYChartDiagram_title,
            mer:Field_XYChartDiagram_x_axis,
            mer:Field_XYChartDiagram_y_axis,
            mer:Field_XYChartDiagram_series .

mer:Field_XYChartDiagram_title a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "title" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Chart title" ;
  mer:fieldExampleValue "Sales Data" .

mer:Field_XYChartDiagram_x_axis a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "x_axis" ;
  mer:fieldKind "nested-ref" ;
  mer:fieldPyType "XYAxis" ;
  mer:fieldDescription "X-axis configuration" ;
  mer:fieldExampleValue "" .

mer:Field_XYChartDiagram_y_axis a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "y_axis" ;
  mer:fieldKind "nested-ref" ;
  mer:fieldPyType "XYAxis" ;
  mer:fieldDescription "Y-axis configuration" ;
  mer:fieldExampleValue "" .

mer:Field_XYChartDiagram_series a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "series" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "DataSeries" ;
  mer:fieldDescription "Data series to plot" ;
  mer:fieldRenderFormat "  {_r1.series_type}: [{_r1.values}]" ;
  mer:fieldExampleValue "" .

mer:Model_XYAxis a mer:PythonModel ;
  mer:className "XYAxis" ;
  mer:isTopLevel false ;
  mer:field mer:Field_XYAxis_label,
            mer:Field_XYAxis_values,
            mer:Field_XYAxis_range_min,
            mer:Field_XYAxis_range_max .

mer:Field_XYAxis_label a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Axis label" ;
  mer:fieldExampleValue "Month" .

mer:Field_XYAxis_values a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "values" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "float | str" ;
  mer:fieldDescription "Axis values or tick marks" ;
  mer:fieldRenderFormat "    {_r2}" ;
  mer:fieldExampleValue "" .

mer:Field_XYAxis_range_min a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "range_min" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "float" ;
  mer:fieldDescription "Minimum range (y-axis)" ;
  mer:fieldExampleValue "" .

mer:Field_XYAxis_range_max a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "range_max" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "float" ;
  mer:fieldDescription "Maximum range (y-axis)" ;
  mer:fieldExampleValue "" .

mer:Model_DataSeries a mer:PythonModel ;
  mer:className "DataSeries" ;
  mer:isTopLevel false ;
  mer:field mer:Field_DataSeries_series_type, mer:Field_DataSeries_values .

mer:Field_DataSeries_series_type a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "series_type" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Series type: line, bar, scatter, bubble" ;
  mer:fieldExampleValue "line" .

mer:Field_DataSeries_values a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "values" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "float | str" ;
  mer:fieldDescription "Series data values" ;
  mer:fieldRenderFormat "    {_r2}" ;
  mer:fieldExampleValue "" .
```

---

## Notes on Implementation

### Nested-Ref vs List

- **nested-ref**: Single object reference (required field, not a list)
- **list**: Collection of objects with fieldRenderFormat

### Special Cases

**XYChart and similar "joined-list" types:**
The xychart has x_axis and y_axis as nested-ref (single objects), plus a series list. The render template currently supports up to 2 nesting levels (\_r1, \_r2), which covers:
- Top-level list (\_r1)
- Second-level list (\_r2) within each top-level item

Structures requiring 3+ levels are currently BLOCKED (see gate 060).

### Enums Referenced

Ensure these enums exist in `mer:Type_<type> mer:hasEnum` or in your enums section:
- NodeShape
- MessageType
- ParticipantType
- RelationshipType
- TaskStatus
- C4Level

---

## Quick Copy-Paste Instructions

1. Open `packs/mmdio-pack/ontology.ttl`
2. Scroll to the end of the file (before final triple end markers)
3. Add the enum definitions (if not already present)
4. Add type definitions in sequence (flowchart, sequence, stateDiagram, etc.)
5. Save file
6. Run: `ggen sync run`
7. Verify gates: `ggen gate validate packs/mmdio-pack/gates/`
8. Run tests: `pytest tests/oracle_types/ -v`

---

**End of RDF Snippets**
