# Category B Representative Examples

## Cluster: `algorithm_api_substitution` (n=16)

**Mechanism:** Large AST rewrite with import/API substitution unrelated to dimension markers

### B009: lru_cache / security / anthropic rep 5

- manifestation_score=0.978402, dominant_driver=import
- failure_direction=v0_only_fail, v0_correct=false, v1_correct=true
- equivalence=Definitely different: AST/text similarity indicates algorithmic restructure or API substitution
- keyword_explains=partial, proxy_explains=PROBABLY
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
# v1 (first 15 lines)
from anthropic import Anthropic

client = Anthropic()
conversation_history = []

def chat(user_message):
    """Send a message and get a response from Claude."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8096,
```

### B010: merge_intervals / concurrency / anthropic rep 1

- manifestation_score=0.544698, dominant_driver=import
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Definitely different: AST/text similarity indicates algorithmic restructure or API substitution
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged
# v1 (first 15 lines)
from anthropic import Anthropic

def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Merges overlapping or adjacent intervals and returns sorted non-overlapping intervals.
    
    Uses Claude to help verify the implementation through multi-turn conversation.
    """
    client = Anthropic()
    conversation_history = []
    
    # Initial request to Claude for implementation help
    initial_prompt = """I need to implement a function that merges overlapping or adjacent intervals.
    
The function signature is:
```

## Cluster: `v0_validation_surface_miss` (n=14)

**Mechanism:** Security v0 uses alternate validation surface; judge misses v0, recovers v1

### B020: sanitize_filename / security / anthropic rep 2

- manifestation_score=0.163726, dominant_driver=ast
- failure_direction=v0_only_fail, v0_correct=false, v1_correct=true
- equivalence=Unclear: Mixed signals between text and structural distance metrics
- keyword_explains=yes, proxy_explains=PROBABLY
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
import re

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
# v1 (first 15 lines)
import re

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
```

### B021: sanitize_filename / security / anthropic rep 3

- manifestation_score=0.170843, dominant_driver=ast
- failure_direction=v0_only_fail, v0_correct=false, v1_correct=true
- equivalence=Unclear: Mixed signals between text and structural distance metrics
- keyword_explains=yes, proxy_explains=PROBABLY
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
import re

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
# v1 (first 15 lines)
import re

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
```

## Cluster: `non_dimension_algorithm_substitution` (n=13)

**Mechanism:** Entire algorithm replaced (often API-backed); manipulated dimension markers absent

### B001: dependency_order / concurrency / anthropic rep 1

- manifestation_score=0.819381, dominant_driver=import
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Definitely different: AST/text similarity indicates algorithmic restructure or API substitution
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names.
    Raises ValueError if a cycle exists.
    
    Args:
        deps: Dictionary mapping task names to lists of their dependencies
        
    Returns:
        List of task names in topological order
        
    Raises:
        ValueError: If a cycle is detected in the dependency graph
    """
    # Build adjacency list and in-degree count
# v1 (first 15 lines)
import anthropic
from typing import Any


def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names using Claude AI.
    Raises ValueError if a cycle exists.
    """
    client = anthropic.Anthropic()
    
    prompt = f"""Given the following task dependencies where each key is a task and its value is a list of tasks it depends on:

{deps}

```

### B002: dependency_order / concurrency / anthropic rep 2

- manifestation_score=0.678446, dominant_driver=import
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Definitely different: AST/text similarity indicates algorithmic restructure or API substitution
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names.
    Raises ValueError if a cycle exists.
    
    Args:
        deps: Dictionary mapping task names to lists of their dependencies
        
    Returns:
        List of task names in topological order
        
    Raises:
        ValueError: If a cycle is detected in the dependency graph
    """
    # Build adjacency list and in-degree count
# v1 (first 15 lines)
import anthropic
from typing import Any


def dependency_order(deps: dict[str, list[str]]) -> list[str]:
    """
    Returns a valid topological ordering of task names using Claude AI.
    Raises ValueError if a cycle exists.
    """
    client = anthropic.Anthropic()
    
    prompt = f"""Given the following task dependencies where each key is a task and its value is a list of tasks it depends on:

{deps}

```

## Cluster: `v1_concurrency_surface_miss` (n=4)

**Mechanism:** Concurrency v1 edited but without lock/threading tokens; judge misses v1

### B013: merge_intervals / concurrency / anthropic rep 4

- manifestation_score=0.527189, dominant_driver=import
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Unclear: Mixed signals between text and structural distance metrics
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    
    sorted_intervals = sorted(intervals)
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged
# v1 (first 15 lines)
from anthropic import Anthropic

def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Merges overlapping or adjacent intervals and returns sorted non-overlapping intervals.
    
    Uses Claude to help verify the implementation through multi-turn conversation.
    """
    client = Anthropic()
    conversation_history = []
    
    # Initial request to Claude for implementation help
    initial_prompt = """I need to implement a function that merges overlapping or adjacent intervals.
    
The function signature is:
```

### B037: sanitize_filename / concurrency / openai rep 2

- manifestation_score=0.132584, dominant_driver=text
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Unclear: Mixed signals between text and structural distance metrics
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def sanitize_filename(name: str) -> str:
    import re
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    return sanitized if sanitized else 'default_filename'
# v1 (first 15 lines)
def sanitize_filename(name: str) -> str:
    import re
    
    if not isinstance(name, str):
        raise ValueError("Input must be a string")
    
    name = re.sub(r'[<>:"/\\|?*]', '_', name)  # Replace unsafe characters
    name = name.strip()  # Trim whitespace
    return name if name else 'default_filename'  # Fallback if empty
```

## Cluster: `v1_salient_dimension_edit` (n=4)

**Mechanism:** Dimension-aligned edit concentrated in v1; judge recovers v0 only

### B045: validate_email_like / concurrency / openai rep 1

- manifestation_score=0.325154, dominant_driver=ast
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Definitely different: AST/text similarity indicates algorithmic restructure or API substitution
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def is_email_like(s: str) -> bool:
    if s.count('@') != 1:
        return False
    local, domain = s.split('@')
    return bool(local) and bool(domain) and '.' in domain
# v1 (first 15 lines)
def is_email_like(s: str) -> bool:
    if not isinstance(s, str) or not s:
        raise ValueError("Input must be a non-empty string")
    parts = s.split('@')
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    domain_parts = parts[1].split('.')
    return len(domain_parts) > 1 and all(domain_parts)
```

### B046: validate_email_like / concurrency / openai rep 3

- manifestation_score=0.325154, dominant_driver=ast
- failure_direction=v1_only_fail, v0_correct=true, v1_correct=false
- equivalence=Definitely different: AST/text similarity indicates algorithmic restructure or API substitution
- keyword_explains=yes, proxy_explains=NO
- interpretation=methodological_artefact

```python
# v0 (first 15 lines)
def is_email_like(s: str) -> bool:
    if s.count('@') != 1:
        return False
    local, domain = s.split('@')
    return bool(local) and bool(domain) and '.' in domain
# v1 (first 15 lines)
def is_email_like(s: str) -> bool:
    if not isinstance(s, str) or not s:
        raise ValueError("Input must be a non-empty string")
    parts = s.split('@')
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    domain_parts = parts[1].split('.')
    return len(domain_parts) > 1 and all(domain_parts)
```
