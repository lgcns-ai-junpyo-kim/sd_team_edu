# 교육 내용 안내

이 문서는 LangChain/LangGraph 입문자를 위한 교재 모음입니다. 각 문서는 **설명 + 이유 + 예제 + 코드**를 포함하며, 실전 설계 관점에서 구성되었습니다.

## 교재 목록

### 01. Agent / Tool / MCP 개요

- [01_agents_tools_mcp](./01_agents_tools_mcp/01_agents_tools_mcp.md): Agent/Tool/MCP의 역할과 관계를 큰 그림에서 정리합니다.
- [02_how_it_works](./01_agents_tools_mcp/02_how_it_works.md): Agent-Tool-MCP 호출 흐름과 실패 처리 위치를 정리합니다.
- [03_architecture_design](./01_agents_tools_mcp/03_architecture_design.md): 아키텍처 레이어 분리와 폴더 구조 설계를 다룹니다.

### 02. LangGraph Agent 기본

- [01_langgraph_agent_basics](./02_langgraph_agent_basics/01_langgraph_agent_basics.md): State/Node/Edge 중심의 LangGraph 핵심 개념을 소개합니다.
- [02_plan_and_execute_agent](./02_langgraph_agent_basics/02_plan_and_execute_agent.md): 계획-실행 분리 구조를 간단한 그래프로 구성합니다.
- [03_planning_concept](./02_langgraph_agent_basics/03_planning_concept.md): 계획 포맷과 검증 규칙을 정리합니다.
- [04_execution_steps](./02_langgraph_agent_basics/04_execution_steps.md): Tool 호출과 결과 저장, 오류 처리 흐름을 설명합니다.
- [05_observe_feedback_loop](./02_langgraph_agent_basics/05_observe_feedback_loop.md): 관찰과 재시도 루프 설계를 다룹니다.

### 03. Tool 설계

- [01_tool_design](./03_tool_design/01_tool_design.md): Tool 설계의 기본 원칙과 최소 인터페이스를 설명합니다.
- [02_tool_examples](./03_tool_design/02_tool_examples.md): 검색/계산/DB 조회 Tool 예시를 제공합니다.
- [03_good_bad_tools](./03_tool_design/03_good_bad_tools.md): 좋은/나쁜 Tool 사례를 비교합니다.
- [04_schema_and_hints](./03_tool_design/04_schema_and_hints.md): 스키마와 힌트 작성 기준을 정리합니다.
- [05_fallback_retry](./03_tool_design/05_fallback_retry.md): 재시도/폴백 전략을 설명합니다.
- [06_extensibility_abstract_class](./03_tool_design/06_extensibility_abstract_class.md): 확장성을 위한 추상 클래스 설계를 다룹니다.

### 04. MCP를 Tool로 사용하기

- [01_mcp_as_tool](./04_mcp_as_tool/01_mcp_as_tool.md): MCP를 Tool 제공자로 보는 관점을 소개합니다.
- [02_what_is_mcp](./04_mcp_as_tool/02_what_is_mcp.md): MCP의 정의와 구성 요소를 설명합니다.
- [03_mcp_vs_msa](./04_mcp_as_tool/03_mcp_vs_msa.md): MCP와 MSA의 목적과 범위를 비교합니다.
- [04_tools_inside_mcp](./04_mcp_as_tool/04_tools_inside_mcp.md): MCP 내부 Tool 관리 방식과 레지스트리를 설명합니다.
- [05_agent_tool_informing_strategies](./04_mcp_as_tool/05_agent_tool_informing_strategies.md): Tool 정보 제공 전략을 비교합니다.
- [06_strategy_read_all_tools](./04_mcp_as_tool/06_strategy_read_all_tools.md): 전체 Tool 제공 전략의 장단점을 정리합니다.
- [07_strategy_partial_tool_reading](./04_mcp_as_tool/07_strategy_partial_tool_reading.md): 필요한 Tool만 부분 제공하는 전략을 설명합니다.
- [08_strategy_tool_info_then_call](./04_mcp_as_tool/08_strategy_tool_info_then_call.md): 호출 직전 상세 정보를 제공하는 전략을 다룹니다.
