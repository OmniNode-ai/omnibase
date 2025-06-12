"""
Parallel Node Introspection Tool

Provides efficient parallel introspection of multiple ONEX nodes simultaneously,
significantly improving performance over sequential introspection.
"""

import asyncio
import importlib
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum


@dataclass
class NodeIntrospectionResult:
    """Result of a single node introspection."""
    node_name: str
    success: bool
    introspection_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    module_path: Optional[str] = None


class ToolParallelIntrospection:
    """
    Tool for performing parallel introspection of multiple ONEX nodes.
    
    Provides significant performance improvements over sequential introspection:
    - Sequential: N × 100ms per node
    - Parallel: ~100ms total for all nodes
    """
    
    def __init__(self, node_id: str = "parallel_introspection_tool"):
        self.node_id = node_id
        self.max_workers = 10  # Limit concurrent introspections
    
    def _introspect_single_node(self, node_name: str, node_version: str = "v1_0_0") -> NodeIntrospectionResult:
        """Introspect a single node (thread-safe operation)."""
        start_time = time.time()
        module_path = f"omnibase.nodes.{node_name}.{node_version}.node"
        
        try:
            # Import the node module
            module = importlib.import_module(module_path)
            
            # Check if introspection is available
            if not hasattr(module, "get_introspection"):
                return NodeIntrospectionResult(
                    node_name=node_name,
                    success=False,
                    error_message="Node does not support introspection",
                    module_path=module_path,
                    response_time_ms=(time.time() - start_time) * 1000
                )
            
            # Get introspection data
            introspection_data = module.get_introspection()
            response_time = (time.time() - start_time) * 1000
            
            return NodeIntrospectionResult(
                node_name=node_name,
                success=True,
                introspection_data=introspection_data,
                module_path=module_path,
                response_time_ms=response_time
            )
            
        except ImportError as e:
            return NodeIntrospectionResult(
                node_name=node_name,
                success=False,
                error_message=f"Failed to import node module: {e}",
                module_path=module_path,
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return NodeIntrospectionResult(
                node_name=node_name,
                success=False,
                error_message=f"Introspection failed: {e}",
                module_path=module_path,
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    async def introspect_nodes_parallel(
        self, 
        node_names: List[str], 
        node_version: str = "v1_0_0",
        correlation_id: Optional[str] = None
    ) -> Dict[str, NodeIntrospectionResult]:
        """
        Introspect multiple nodes in parallel for optimal performance.
        
        Args:
            node_names: List of node names to introspect
            node_version: Version of nodes to introspect (default: v1_0_0)
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            Dictionary mapping node names to introspection results
        """
        start_time = time.time()
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[ToolParallelIntrospection] Starting parallel introspection of {len(node_names)} nodes",
            node_id=self.node_id,
            context={"correlation_id": correlation_id, "node_count": len(node_names)}
        )
        
        # Use ThreadPoolExecutor for CPU-bound introspection operations
        loop = asyncio.get_event_loop()
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all introspection tasks
            future_to_node = {
                loop.run_in_executor(
                    executor, 
                    self._introspect_single_node, 
                    node_name, 
                    node_version
                ): node_name
                for node_name in node_names
            }
            
            # Collect results as they complete
            completed_futures = await asyncio.gather(*future_to_node.keys(), return_exceptions=True)
            
            for i, result in enumerate(completed_futures):
                node_name = list(future_to_node.values())[i]
                
                if isinstance(result, Exception):
                    # Handle unexpected executor errors
                    results[node_name] = NodeIntrospectionResult(
                        node_name=node_name,
                        success=False,
                        error_message=f"Executor error: {result}",
                        response_time_ms=(time.time() - start_time) * 1000
                    )
                elif isinstance(result, NodeIntrospectionResult):
                    results[node_name] = result
                    
                    if result.success:
                        emit_log_event_sync(
                            LogLevelEnum.DEBUG,
                            f"[ToolParallelIntrospection] ✓ {node_name} introspection completed in {result.response_time_ms:.1f}ms",
                            node_id=self.node_id,
                            context={"correlation_id": correlation_id, "node_name": node_name}
                        )
                    else:
                        emit_log_event_sync(
                            LogLevelEnum.WARNING,
                            f"[ToolParallelIntrospection] ✗ {node_name} introspection failed: {result.error_message}",
                            node_id=self.node_id,
                            context={"correlation_id": correlation_id, "node_name": node_name}
                        )
                else:
                    # Unexpected result type
                    results[node_name] = NodeIntrospectionResult(
                        node_name=node_name,
                        success=False,
                        error_message=f"Unexpected result type: {type(result)}",
                        response_time_ms=(time.time() - start_time) * 1000
                    )
        
        total_time = (time.time() - start_time) * 1000
        successful_count = sum(1 for r in results.values() if r.success)
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[ToolParallelIntrospection] Parallel introspection completed: {successful_count}/{len(node_names)} successful in {total_time:.1f}ms",
            node_id=self.node_id,
            context={
                "correlation_id": correlation_id,
                "total_time_ms": total_time,
                "successful_count": successful_count,
                "total_count": len(node_names)
            }
        )
        
        return results
    
    def discover_available_nodes(self, nodes_directory: Path = None) -> List[str]:
        """
        Discover all available ONEX nodes in the nodes directory.
        
        Args:
            nodes_directory: Path to nodes directory (default: src/omnibase/nodes)
            
        Returns:
            List of discovered node names
        """
        if nodes_directory is None:
            nodes_directory = Path("src/omnibase/nodes")
        
        discovered_nodes = []
        
        if not nodes_directory.exists():
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"[ToolParallelIntrospection] Nodes directory not found: {nodes_directory}",
                node_id=self.node_id
            )
            return discovered_nodes
        
        for node_dir in nodes_directory.iterdir():
            if not node_dir.is_dir() or node_dir.name.startswith("."):
                continue
                
            # Check if node has a v1_0_0 directory with node.py
            v1_dir = node_dir / "v1_0_0"
            if v1_dir.exists() and (v1_dir / "node.py").exists():
                discovered_nodes.append(node_dir.name)
        
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[ToolParallelIntrospection] Discovered {len(discovered_nodes)} nodes: {', '.join(discovered_nodes)}",
            node_id=self.node_id,
            context={"discovered_count": len(discovered_nodes)}
        )
        
        return discovered_nodes
    
    async def introspect_all_nodes(
        self, 
        nodes_directory: Path = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, NodeIntrospectionResult]:
        """
        Discover and introspect all available ONEX nodes in parallel.
        
        Args:
            nodes_directory: Path to nodes directory (default: src/omnibase/nodes)
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            Dictionary mapping node names to introspection results
        """
        # Discover all available nodes
        node_names = self.discover_available_nodes(nodes_directory)
        
        if not node_names:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                "[ToolParallelIntrospection] No nodes discovered for introspection",
                node_id=self.node_id,
                context={"correlation_id": correlation_id}
            )
            return {}
        
        # Introspect all discovered nodes in parallel
        return await self.introspect_nodes_parallel(node_names, correlation_id=correlation_id)
    
    def get_performance_summary(self, results: Dict[str, NodeIntrospectionResult]) -> Dict[str, Any]:
        """Get performance summary of introspection results."""
        if not results:
            return {"total_nodes": 0}
        
        response_times = [r.response_time_ms for r in results.values() if r.response_time_ms is not None]
        successful_count = sum(1 for r in results.values() if r.success)
        
        return {
            "total_nodes": len(results),
            "successful_count": successful_count,
            "failed_count": len(results) - successful_count,
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "success_rate": (successful_count / len(results)) * 100 if results else 0
        } 