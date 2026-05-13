from dataclasses import dataclass, field


@dataclass
class NavigationEntry:
    section: str
    context: dict


@dataclass
class SessionContext:
    user_id: str
    current_section: str = "main_menu"
    context: dict = field(default_factory=dict)
    navigation_stack: list[NavigationEntry] = field(default_factory=list)
    
    def push_state(self, section: str, context: dict | None = None):
        self.navigation_stack.append(NavigationEntry(
            section=self.current_section,
            context=dict(self.context)
        ))
        self.current_section = section
        self.context = context or {}
    
    def pop_state(self) -> NavigationEntry | None:
        if not self.navigation_stack:
            return None
        entry = self.navigation_stack.pop()
        self.current_section = entry.section
        self.context = entry.context
        return entry
    
    def clear_stack(self):
        self.navigation_stack.clear()
        self.current_section = "main_menu"
        self.context = {}