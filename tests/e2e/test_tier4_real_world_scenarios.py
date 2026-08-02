"""
Tier 4 Real-World Application Scenario E2E Test Suite for mmdio.

Tests cover complex, end-to-end multi-step application scenarios across 10+ real-world domains:
1. Scenario 1: Microservices Architecture C4 Context Diagram (parse/AST modify/render/oracle verify).
2. Scenario 2: Git Feature Branch & Release Workflow (parse/AST modify/render/oracle verify).
3. Scenario 3: Complex Project Gantt Schedule with Milestones and Dependencies.
4. Scenario 4: E-Commerce Database Entity-Relationship Schema.
5. Scenario 5: Agile Sprint Kanban Project Board with Card Columns.
6. Scenario 6: Product Roadmap Timeline with Milestones.
7. Scenario 7: Financial Data XY Chart (bar & line series).
8. Scenario 8: Enterprise System Sequence Diagram with Autonumber & Participants.
9. Scenario 9: Supply Chain Sankey Flow Network.
10. Scenario 10: Multi-Module Software Class Hierarchy with Inheritance & Associations.
11. Scenario 11: Infrastructure Grid Block Diagram Layout.
12. Scenario 12: Multi-Diagram AST Roundtrip Verification Suite.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

# Ensure project root & src are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Avoid circular import issues by loading engine.render first
import mmdio.engine.render

from tests.e2e.conftest import validate_mermaid_source

from mmdio.engine.models import (
    Block, BlockDiagram, Connection,
    C4Diagram, C4Element, C4Relationship,
    ClassDefinition, ClassDiagram, ClassMember, ClassMethod, ClassRelationship,
    DataSeries,
    ERAttribute, ERDiagram, EREntity, ERRelationship,
    FlowchartDiagram, FlowchartEdge, FlowchartNode,
    GanttChart, GanttDependency, GanttTask,
    GitBranch, GitCommit, GitGraph,
    KanbanCard, KanbanDiagram, KanbanSection,
    Mindmap, MindmapNode,
    PieChart, PieSlice,
    SankeyDiagram, SankeyFlow,
    SequenceDiagram, SequenceMessage, SequenceParticipant,
    StateDiagram, StateNode, StateTransition,
    TimelineDiagram, TimelineEvent,
    XYAxis, XYChartDiagram
)
from mmdio.engine.enums import (
    NodeShape, MessageType, RelationshipType, CardinityType, TaskStatus, C4Level, ParticipantType
)
from mmdio.engine.render import (
    render_diagram, render_c4, render_git, render_gantt, render_er, render_kanban,
    render_timeline, render_xychart, render_sequence, render_sankey, render_class,
    render_block, render_flowchart, render_pie, render_state
)
from mmdio.engine.parser import parse_sequence, parse_flowchart, parse_c4, parse_state


class TestTier4RealWorldScenarios:
    """Test class implementing Tier 4 Real-World Application Scenario E2E tests."""

    def test_scenario_1_microservices_c4_context(self) -> None:
        """
        Scenario 1: Microservices Architecture C4 Context Diagram.
        Workflow:
        1. Construct/parse C4 System Context AST with Person, Systems, Containers.
        2. Verify initial AST structure.
        3. AST Modify: Add new container (Order Database, PostgreSQL) and relationship (API Gateway -> DB via JDBC).
        4. Render AST to Mermaid text.
        5. Verify rendered output against Node.js Mermaid oracle.
        """
        c4_ast = C4Diagram(
            title="Banking Microservices Architecture",
            level=C4Level.C1,
            elements=[
                C4Element(id="cust", name="Banking Customer", type="Person", description="Customer using web/mobile banking"),
                C4Element(id="gateway", name="API Gateway", type="Container", description="Routes and authenticates incoming REST calls"),
                C4Element(id="auth_svc", name="Auth Service", type="Container", description="Issues JWT tokens"),
                C4Element(id="order_svc", name="Order Service", type="Container", description="Processes customer orders"),
            ],
            relationships=[
                C4Relationship(source="cust", target="gateway", label="HTTPS / REST"),
                C4Relationship(source="gateway", target="auth_svc", label="Validates auth tokens via gRPC"),
                C4Relationship(source="gateway", target="order_svc", label="Forwards order requests"),
            ]
        )

        assert len(c4_ast.elements) == 4
        assert len(c4_ast.relationships) == 3

        # AST Modify: Add Order DB container and relationship
        db_container = C4Element(
            id="order_db",
            name="Order Database",
            type="Container",
            description="Persists order state and history in PostgreSQL"
        )
        db_rel = C4Relationship(
            source="order_svc",
            target="order_db",
            label="Reads/Writes order data via JDBC"
        )
        c4_ast.elements.append(db_container)
        c4_ast.relationships.append(db_rel)

        assert len(c4_ast.elements) == 5
        assert len(c4_ast.relationships) == 4

        # Render diagram
        rendered = render_c4(c4_ast)
        assert "C4Context" in rendered
        assert "Order Database" in rendered
        assert "JDBC" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: c4" in oracle_res

    def test_scenario_2_git_feature_branch_workflow(self) -> None:
        """
        Scenario 2: Git Feature Branch & Release Workflow.
        Workflow:
        1. Construct GitGraph AST representing main branch commit history.
        2. AST Modify: Add feature commits and release candidate tags.
        3. Render AST to Mermaid text string.
        4. Verify output with Node.js Mermaid oracle.
        """
        git_ast = GitGraph(
            main_branch="main",
            commits=[
                GitCommit(id="c1", message="Initial repository commit"),
                GitCommit(id="c2", message="Setup base framework"),
            ]
        )

        assert git_ast.main_branch == "main"
        assert len(git_ast.commits) == 2

        # AST Modify: Add feature commits and release tag
        commit_3 = GitCommit(id="c3", message="Implement OAuth2 provider integration")
        commit_4 = GitCommit(id="c4", message="Add PKCE challenge validation")
        release_commit = GitCommit(id="c5", message="Release candidate v2.0-rc1")

        git_ast.commits.extend([commit_3, commit_4, release_commit])

        assert len(git_ast.commits) == 5

        # Render diagram
        rendered = render_git(git_ast)
        assert "gitGraph" in rendered
        assert "c1" in rendered
        assert "c5" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: gitGraph" in oracle_res

    def test_scenario_3_complex_project_gantt_schedule(self) -> None:
        """
        Scenario 3: Complex Project Gantt Schedule with Milestones and Dependencies.
        Workflow:
        1. Construct GanttChart AST with multi-phase project schedule.
        2. AST Modify: Add Milestone task with dependencies.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        gantt_ast = GanttChart(
            title="Enterprise ERP System Migration",
            date_format="YYYY-MM-DD",
            tasks=[
                GanttTask(id="p1", title="Legacy Data Audit", status=TaskStatus.DONE, start_date="2026-03-01", end_date="14d"),
                GanttTask(id="p2", title="Schema Mapping ETL", status=TaskStatus.ACTIVE, start_date="2026-03-15", end_date="21d", dependencies=[GanttDependency(task_id="p1")]),
                GanttTask(id="p3", title="UAT Testing", status=TaskStatus.ACTIVE, start_date="2026-04-05", end_date="10d", dependencies=[GanttDependency(task_id="p2")]),
            ]
        )

        assert len(gantt_ast.tasks) == 3

        # AST Modify: Add Milestone task dependent on UAT testing (p3)
        milestone_task = GanttTask(
            id="m1",
            title="Production Cutover Signoff",
            status=TaskStatus.MILESTONE,
            start_date="2026-04-15",
            end_date="0d",
            dependencies=[GanttDependency(task_id="p3")]
        )
        gantt_ast.tasks.append(milestone_task)

        assert len(gantt_ast.tasks) == 4

        # Render diagram
        rendered = render_gantt(gantt_ast)
        assert "gantt" in rendered
        assert "m1 : milestone" in rendered
        assert "p1 : done" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: gantt" in oracle_res

    def test_scenario_4_ecommerce_er_database_schema(self) -> None:
        """
        Scenario 4: E-Commerce Database Entity-Relationship Schema.
        Workflow:
        1. Construct ERDiagram AST with CUSTOMER, ORDER, LINE_ITEM entities and relationships.
        2. AST Modify: Add PAYMENT entity with attributes (payment_id, order_id, amount) and relationship ORDER -> PAYMENT.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        er_ast = ERDiagram(
            entities=[
                EREntity(name="CUSTOMER", attributes=[
                    ERAttribute(name="customer_id", attr_type="uuid"),
                    ERAttribute(name="email", attr_type="string"),
                ]),
                EREntity(name="ORDER", attributes=[
                    ERAttribute(name="order_id", attr_type="uuid"),
                    ERAttribute(name="customer_id", attr_type="uuid"),
                    ERAttribute(name="total_amount", attr_type="decimal")
                ]),
                EREntity(name="LINE_ITEM", attributes=[
                    ERAttribute(name="item_id", attr_type="uuid"),
                    ERAttribute(name="order_id", attr_type="uuid"),
                    ERAttribute(name="quantity", attr_type="int")
                ])
            ],
            relationships=[
                ERRelationship(entity_a="CUSTOMER", entity_b="ORDER", cardinality_a="||", cardinality_b="o{", relation_type=RelationshipType.ASSOCIATION),
                ERRelationship(entity_a="ORDER", entity_b="LINE_ITEM", cardinality_a="||", cardinality_b="|{", relation_type=RelationshipType.ASSOCIATION)
            ]
        )

        assert len(er_ast.entities) == 3
        assert len(er_ast.relationships) == 2

        # AST Modify: Add PAYMENT entity & relationship
        payment_entity = EREntity(
            name="PAYMENT",
            attributes=[
                ERAttribute(name="payment_id", attr_type="uuid"),
                ERAttribute(name="order_id", attr_type="uuid"),
                ERAttribute(name="amount", attr_type="decimal"),
                ERAttribute(name="status", attr_type="string")
            ]
        )
        payment_rel = ERRelationship(
            entity_a="ORDER",
            entity_b="PAYMENT",
            cardinality_a="||",
            cardinality_b="o{",
            relation_type=RelationshipType.ASSOCIATION
        )
        er_ast.entities.append(payment_entity)
        er_ast.relationships.append(payment_rel)

        assert len(er_ast.entities) == 4
        assert len(er_ast.relationships) == 3

        # Render diagram
        rendered = render_er(er_ast)
        assert "erDiagram" in rendered
        assert "CUSTOMER" in rendered
        assert "PAYMENT" in rendered
        assert "payment_id" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: er" in oracle_res

    def test_scenario_5_agile_sprint_kanban_board(self) -> None:
        """
        Scenario 5: Agile Sprint Kanban Project Board with Card Columns.
        Workflow:
        1. Construct KanbanDiagram AST with columns (To Do, In Progress, Code Review, Done).
        2. AST Modify: Move card from 'To Do' to 'In Progress', add new card to 'Code Review'.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        kanban_ast = KanbanDiagram(
            sections=[
                KanbanSection(
                    name="To Do",
                    cards=[
                        KanbanCard(title="Implement OAuth Refresh Endpoint"),
                        KanbanCard(title="Add Redis Rate Limiter")
                    ]
                ),
                KanbanSection(
                    name="In Progress",
                    cards=[
                        KanbanCard(title="Refactor Parser Dispatcher")
                    ]
                ),
                KanbanSection(
                    name="Code Review",
                    cards=[]
                ),
                KanbanSection(
                    name="Done",
                    cards=[
                        KanbanCard(title="Setup Repository Infrastructure")
                    ]
                )
            ]
        )

        assert len(kanban_ast.sections) == 4
        assert len(kanban_ast.sections[0].cards) == 2

        # AST Modify: Move card from To Do -> In Progress
        moved_card = kanban_ast.sections[0].cards.pop(0)
        kanban_ast.sections[1].cards.append(moved_card)

        # Add new card to Code Review
        new_card = KanbanCard(title="Write Tier 4 E2E Test Suite")
        kanban_ast.sections[2].cards.append(new_card)

        assert len(kanban_ast.sections[0].cards) == 1
        assert len(kanban_ast.sections[1].cards) == 2
        assert len(kanban_ast.sections[2].cards) == 1

        # Render diagram
        rendered = render_kanban(kanban_ast)
        assert "kanban" in rendered
        assert "section To Do" in rendered
        assert "section In Progress" in rendered
        assert "Implement OAuth Refresh Endpoint" in rendered
        assert "Write Tier 4 E2E Test Suite" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: kanban" in oracle_res

    def test_scenario_6_product_roadmap_timeline(self) -> None:
        """
        Scenario 6: Product Roadmap Timeline with Milestones.
        Workflow:
        1. Construct TimelineDiagram AST with Q1, Q2, Q3 2026 events.
        2. AST Modify: Add Q4 2026 event ('Global Multi-Region Deployment').
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        timeline_ast = TimelineDiagram(
            title="SaaS Product Roadmap 2026",
            events=[
                TimelineEvent(time="Q1 2026", description="Developer API v1 Release"),
                TimelineEvent(time="Q2 2026", description="GraphQL & WebSocket Support"),
                TimelineEvent(time="Q3 2026", description="SOC2 Type II Security Compliance")
            ]
        )

        assert len(timeline_ast.events) == 3

        # AST Modify: Add Q4 2026 event
        timeline_ast.events.append(
            TimelineEvent(time="Q4 2026", description="Global Multi-Region Deployment")
        )

        assert len(timeline_ast.events) == 4

        # Render diagram
        rendered = render_timeline(timeline_ast)
        assert "timeline" in rendered
        assert "SaaS Product Roadmap 2026" in rendered
        assert "Q4 2026 : Global Multi-Region Deployment" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: timeline" in oracle_res

    def test_scenario_7_financial_data_xychart(self) -> None:
        """
        Scenario 7: Financial Data XY Chart (bar & line series).
        Workflow:
        1. Construct XYChartDiagram AST with quarterly revenue bar series and operating profit line series.
        2. AST Modify: Add Net Income Margin line series.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        xy_ast = XYChartDiagram(
            title="FY2026 Quarterly Financial Results ($M)",
            x_axis=XYAxis(label="Quarters", values=["Q1", "Q2", "Q3", "Q4"]),
            y_axis=XYAxis(label="USD Millions", range_min=0, range_max=250),
            series=[
                DataSeries(series_type="bar", values=[120.0, 145.0, 180.0, 210.0]),
                DataSeries(series_type="line", values=[35.0, 48.0, 62.0, 85.0])
            ]
        )

        assert len(xy_ast.series) == 2

        # AST Modify: Add Net Income Margin line series
        xy_ast.series.append(
            DataSeries(series_type="line", values=[25.0, 32.0, 45.0, 60.0])
        )

        assert len(xy_ast.series) == 3

        # Render diagram
        rendered = render_xychart(xy_ast)
        assert "xychart-beta" in rendered
        assert "bar:" in rendered
        assert "line:" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: xychart" in oracle_res

    def test_scenario_8_enterprise_system_sequence(self) -> None:
        """
        Scenario 8: Enterprise System Sequence Diagram with Autonumber & Participants.
        Workflow:
        1. Parse or construct SequenceDiagram AST with actors, participants, sync/async/return messages.
        2. AST Modify: Add audit logging message to AuditService.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        seq_ast = SequenceDiagram(
            title="Order Checkout Sequence",
            participants=[
                SequenceParticipant(id="client", name="Client Web App", participant_type=ParticipantType.ACTOR),
                SequenceParticipant(id="gateway", name="API Gateway", participant_type=ParticipantType.PARTICIPANT),
                SequenceParticipant(id="auth", name="Auth Server", participant_type=ParticipantType.PARTICIPANT),
                SequenceParticipant(id="db", name="User DB", participant_type=ParticipantType.PARTICIPANT),
            ],
            messages=[
                SequenceMessage(from_id="client", to_id="gateway", label="POST /checkout", message_type=MessageType.SYNC, sequence_number=1),
                SequenceMessage(from_id="gateway", to_id="auth", label="Validate Token", message_type=MessageType.SYNC, sequence_number=2),
                SequenceMessage(from_id="auth", to_id="db", label="Query Permissions", message_type=MessageType.SYNC, sequence_number=3),
                SequenceMessage(from_id="db", to_id="auth", label="Permissions OK", message_type=MessageType.RETURN, sequence_number=4),
            ]
        )

        assert len(seq_ast.participants) == 4
        assert len(seq_ast.messages) == 4

        # AST Modify: Add Audit logging message
        seq_ast.messages.append(
            SequenceMessage(
                from_id="gateway",
                to_id="db",
                label="Write Transaction Log",
                message_type=MessageType.SYNC,
                sequence_number=5
            )
        )

        assert len(seq_ast.messages) == 5

        # Render diagram
        rendered = render_sequence(seq_ast)
        assert "sequenceDiagram" in rendered
        assert "Write Transaction Log" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: sequence" in oracle_res

    def test_scenario_9_supply_chain_sankey_flow(self) -> None:
        """
        Scenario 9: Supply Chain Sankey Flow Network.
        Workflow:
        1. Construct SankeyDiagram AST representing green energy supply chain flows.
        2. AST Modify: Add Biomass energy flow into Grid Storage.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        sankey_ast = SankeyDiagram(
            flows=[
                SankeyFlow(source="Solar Energy", target="Grid Storage", value=320.5),
                SankeyFlow(source="Wind Turbines", target="Grid Storage", value=210.0),
                SankeyFlow(source="Hydroelectric", target="Grid Storage", value=145.0),
                SankeyFlow(source="Grid Storage", target="Industrial Sector", value=400.0),
                SankeyFlow(source="Grid Storage", target="Residential Sector", value=275.5),
            ]
        )

        assert len(sankey_ast.flows) == 5

        # AST Modify: Add Biomass energy flow
        sankey_ast.flows.append(
            SankeyFlow(source="Biomass Energy", target="Grid Storage", value=65.0)
        )

        assert len(sankey_ast.flows) == 6

        # Render diagram
        rendered = render_sankey(sankey_ast)
        assert "sankey-beta" in rendered
        assert "Biomass Energy,Grid Storage,65" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: sankey" in oracle_res

    def test_scenario_10_multi_module_software_class_hierarchy(self) -> None:
        """
        Scenario 10: Multi-Module Software Class Hierarchy with Inheritance & Associations.
        Workflow:
        1. Construct ClassDiagram AST representing software architecture interfaces and concrete implementations.
        2. AST Modify: Add CachedRepository subclass inheriting from SqlRepository with INHERITANCE relationship.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        class_ast = ClassDiagram(
            classes=[
                ClassDefinition(
                    name="Repository",
                    methods=[
                        ClassMethod(name="find_by_id", signature="(id: str)", return_type="Entity", visibility="+"),
                        ClassMethod(name="save", signature="(entity: Entity)", return_type="bool", visibility="+")
                    ]
                ),
                ClassDefinition(
                    name="SqlRepository",
                    members=[
                        ClassMember(name="db_conn", type="DbConnection", visibility="-")
                    ],
                    methods=[
                        ClassMethod(name="find_by_id", signature="(id: str)", return_type="Entity", visibility="+")
                    ]
                ),
                ClassDefinition(
                    name="UserService",
                    members=[
                        ClassMember(name="repo", type="Repository", visibility="-")
                    ],
                    methods=[
                        ClassMethod(name="get_user", signature="(user_id: str)", return_type="User", visibility="+")
                    ]
                )
            ],
            relationships=[
                ClassRelationship(from_class="SqlRepository", to_class="Repository", type=RelationshipType.REALIZATION, label="implements"),
                ClassRelationship(from_class="UserService", to_class="Repository", type=RelationshipType.ASSOCIATION, label="uses")
            ]
        )

        assert len(class_ast.classes) == 3
        assert len(class_ast.relationships) == 2

        # AST Modify: Add CachedRepository extending SqlRepository
        cached_repo = ClassDefinition(
            name="CachedRepository",
            members=[
                ClassMember(name="redis_client", type="RedisCache", visibility="-")
            ],
            methods=[
                ClassMethod(name="clear_cache", signature="()", return_type="void", visibility="+")
            ]
        )
        inheritance_rel = ClassRelationship(
            from_class="CachedRepository",
            to_class="SqlRepository",
            type=RelationshipType.INHERITANCE,
            label="extends"
        )
        class_ast.classes.append(cached_repo)
        class_ast.relationships.append(inheritance_rel)

        assert len(class_ast.classes) == 4
        assert len(class_ast.relationships) == 3

        # Render diagram
        rendered = render_class(class_ast)
        assert "classDiagram" in rendered
        assert "CachedRepository" in rendered
        assert "SqlRepository" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: class" in oracle_res

    def test_scenario_11_kubernetes_infrastructure_block_grid(self) -> None:
        """
        Scenario 11: Kubernetes Cluster Infrastructure Block Grid Diagram.
        Workflow:
        1. Construct BlockDiagram AST with 4 columns layout representing K8s cluster infrastructure.
        2. AST Modify: Add Redis Cache block and connection.
        3. Render AST to Mermaid text.
        4. Verify output with Node.js Mermaid oracle.
        """
        block_ast = BlockDiagram(
            columns=4,
            blocks=[
                Block(id="ingress", label="Nginx Ingress Controller"),
                Block(id="web", label="Web Portal Frontend"),
                Block(id="api", label="Backend REST API"),
                Block(id="db", label="PostgreSQL Primary Database"),
            ],
            connections=[
                Connection(source="ingress", target="web", arrow_type="-->"),
                Connection(source="web", target="api", arrow_type="-->"),
                Connection(source="api", target="db", arrow_type="-->"),
            ]
        )

        assert block_ast.columns == 4
        assert len(block_ast.blocks) == 4
        assert len(block_ast.connections) == 3

        # AST Modify: Add Redis cache block and API connection
        cache_block = Block(id="cache", label="Redis Distributed Cache")
        cache_conn = Connection(source="api", target="cache", arrow_type="-->")
        block_ast.blocks.append(cache_block)
        block_ast.connections.append(cache_conn)

        assert len(block_ast.blocks) == 5
        assert len(block_ast.connections) == 4

        # Render diagram
        rendered = render_block(block_ast)
        assert "block-beta" in rendered
        assert "columns 4" in rendered
        assert "Redis Distributed Cache" in rendered

        # Oracle verify
        oracle_res = validate_mermaid_source(rendered)
        assert "SUCCESS: Detected diagram type: block" in oracle_res

    def test_scenario_12_multi_diagram_ast_mutation_suite(self) -> None:
        """
        Scenario 12: Multi-Diagram AST Roundtrip Verification Suite across Flowchart, State, and Pie diagrams.
        Workflow:
        1. Construct Flowchart, State, and Pie diagram ASTs.
        2. Mutate each AST model (add nodes, transitions, slices).
        3. Render all 3 diagrams.
        4. Verify each rendered diagram against Node.js Mermaid oracle.
        """
        # Flowchart
        fc_ast = FlowchartDiagram(
            direction="LR",
            nodes=[
                FlowchartNode(id="A", label="Input Request", node_type=NodeShape.RECTANGLE),
                FlowchartNode(id="B", label="Validate Payload", node_type=NodeShape.DIAMOND),
            ],
            edges=[
                FlowchartEdge(source="A", target="B", label="Parse JSON")
            ]
        )

        # State Diagram
        state_ast = StateDiagram(
            states=[
                StateNode(id="Idle", label="Idle State"),
                StateNode(id="Processing", label="Processing Request"),
            ],
            transitions=[
                StateTransition(source="Idle", target="Processing", label="recv_req")
            ]
        )

        # Pie Chart
        pie_ast = PieChart(
            title="Cloud Resource Distribution",
            slices=[
                PieSlice(label="Compute (EC2 / EKS)", value=55.0),
                PieSlice(label="Storage (S3 / EBS)", value=30.0),
                PieSlice(label="Networking & CDN", value=15.0)
            ]
        )

        # Mutate ASTs
        fc_ast.nodes.append(FlowchartNode(id="C", label="Save to DB", node_type=NodeShape.CYLINDER))
        fc_ast.edges.append(FlowchartEdge(source="B", target="C", label="Valid"))

        state_ast.states.append(StateNode(id="Completed", label="Request Completed"))
        state_ast.transitions.append(StateTransition(source="Processing", target="Completed", label="finish"))

        pie_ast.slices.append(PieSlice(label="Monitoring & Security", value=10.0))

        # Render and verify with oracle
        rendered_fc = render_flowchart(fc_ast)
        oracle_fc = validate_mermaid_source(rendered_fc)
        assert "SUCCESS: Detected diagram type: flowchart" in oracle_fc

        rendered_state = render_state(state_ast)
        oracle_state = validate_mermaid_source(rendered_state)
        assert "SUCCESS: Detected diagram type:" in oracle_state

        rendered_pie = render_pie(pie_ast)
        oracle_pie = validate_mermaid_source(rendered_pie)
        assert "SUCCESS: Detected diagram type: pie" in oracle_pie
