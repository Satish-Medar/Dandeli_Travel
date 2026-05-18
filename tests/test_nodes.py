# Tests travel agent routing and booking node behavior.
# File: tests/test_nodes.py


"""Unit tests for agent nodes."""
import pytest
from travel_agents.nodes import (
    researcher_node,
    planner_node,
    booker_node,
    router_node
)
from travel_agents.state import GraphState


class TestRouterNode:
    """Test the router node that classifies intent."""
    
    def test_router_identifies_search_intent(self):
        """Test router identifies search queries."""
        state = GraphState(
            messages=[("user", "Find resorts with pool and wifi")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = router_node(state)
        assert result['next_node'] == "researcher"
    
    def test_router_identifies_planning_intent(self):
        """Test router identifies trip planning queries."""
        state = GraphState(
            messages=[("user", "Plan a 2-day trip with rafting")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = router_node(state)
        assert result['next_node'] == "planner"
    
    def test_router_identifies_booking_intent(self):
        """Test router identifies booking queries."""
        state = GraphState(
            messages=[("user", "Book this resort for me")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = router_node(state)
        assert result['next_node'] == "booker"
    
    def test_router_identifies_smalltalk(self):
        """Test router identifies smalltalk."""
        state = GraphState(
            messages=[("user", "Hello, how are you?")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = router_node(state)
        assert result['next_node'] == "smalltalk"
    
    def test_router_handles_empty_messages(self):
        """Test router handles empty messages."""
        state = GraphState(
            messages=[],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = router_node(state)
        # Should handle gracefully
        assert 'next_node' in result
    
    def test_router_handles_multiple_messages(self):
        """Test router with multiple messages."""
        state = GraphState(
            messages=[
                ("user", "Hello"),
                ("assistant", "Hi there!"),
                ("user", "Find resorts with pool")
            ],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = router_node(state)
        # Should classify based on last user message
        assert result['next_node'] == "researcher"


class TestResearcherNode:
    """Test the researcher node."""
    
    @pytest.mark.asyncio
    async def test_researcher_node_returns_response(self):
        """Test researcher node returns a response."""
        state = GraphState(
            messages=[("user", "Find resorts with pool")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await researcher_node(state)
        assert 'response' in result
        assert len(result['response']) > 0
    
    @pytest.mark.asyncio
    async def test_researcher_node_with_filters(self):
        """Test researcher node with specific filters."""
        state = GraphState(
            messages=[("user", "Find resorts with pool and wifi under 8000")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await researcher_node(state)
        assert 'response' in result
        # Response should mention pool/wifi or budget
        response_text = result['response'].lower()
        assert any(word in response_text for word in ['pool', 'wifi', 'resort', 'budget'])
    
    @pytest.mark.asyncio
    async def test_researcher_node_handles_empty_query(self):
        """Test researcher node handles empty query."""
        state = GraphState(
            messages=[("user", "")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await researcher_node(state)
        assert 'response' in result


class TestPlannerNode:
    """Test the planner node."""
    
    @pytest.mark.asyncio
    async def test_planner_node_returns_itinerary(self):
        """Test planner node creates trip itinerary."""
        state = GraphState(
            messages=[("user", "Plan a 2-day trip with rafting")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await planner_node(state)
        assert 'response' in result
        assert len(result['response']) > 0
    
    @pytest.mark.asyncio
    async def test_planner_node_includes_activities(self):
        """Test planner includes requested activities."""
        state = GraphState(
            messages=[("user", "Plan a trip with rafting and nature walks")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await planner_node(state)
        response_text = result['response'].lower()
        # Should mention rafting or nature activities
        assert any(word in response_text for word in ['rafting', 'nature', 'walk', 'day', 'itinerary'])
    
    @pytest.mark.asyncio
    async def test_planner_node_handles_different_durations(self):
        """Test planner handles different trip durations."""
        state = GraphState(
            messages=[("user", "Plan a 3-day trip")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await planner_node(state)
        assert 'response' in result


class TestBookerNode:
    """Test the booker node."""
    
    @pytest.mark.asyncio
    async def test_booker_node_handles_booking_request(self):
        """Test booker node processes booking requests."""
        state = GraphState(
            messages=[("user", "Book River Valley for 2 nights")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await booker_node(state)
        assert 'response' in result
        assert len(result['response']) > 0
    
    @pytest.mark.asyncio
    async def test_booker_node_requires_resort_info(self):
        """Test booker node handles missing resort info."""
        state = GraphState(
            messages=[("user", "Book a resort")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await booker_node(state)
        assert 'response' in result


class TestNodeErrorHandling:
    """Test error handling in nodes."""
    
    @pytest.mark.asyncio
    async def test_nodes_handle_missing_state_fields(self):
        """Test nodes handle missing state fields gracefully."""
        # State with missing fields
        state = GraphState(
            messages=[("user", "Find resorts")],
            session_id=None,
            user_id=None,
            history=None
        )
        
        result = await researcher_node(state)
        assert 'response' in result
    
    @pytest.mark.asyncio
    async def test_nodes_handle_invalid_messages(self):
        """Test nodes handle invalid message formats."""
        state = GraphState(
            messages=[("invalid", "format")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        result = await researcher_node(state)
        assert 'response' in result


class TestNodeIntegration:
    """Test nodes work together."""
    
    @pytest.mark.asyncio
    async def test_researcher_then_planner_flow(self):
        """Test researcher and planner work in sequence."""
        # First researcher finds resorts
        research_state = GraphState(
            messages=[("user", "Find resorts with pool")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        research_result = await researcher_node(research_state)
        assert 'response' in research_result
        
        # Then planner creates itinerary
        plan_state = GraphState(
            messages=[("user", "Plan a 2-day trip with rafting")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )
        
        plan_result = await planner_node(plan_state)
        assert 'response' in plan_result
        
        # Both should produce different responses
        assert research_result['response'] != plan_result['response']