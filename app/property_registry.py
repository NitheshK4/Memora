from typing import Dict, Any, Optional

class PropertyDefinition:
    def __init__(
        self,
        name: str,
        stable: bool = False,
        multi_value: bool = False,
        expected_type: str = "string",
        resolution_strategy: str = "recency",  # recency, dispute, merge, confidence
        description: str = ""
    ):
        self.name = name
        self.stable = stable
        self.multi_value = multi_value
        self.expected_type = expected_type
        self.resolution_strategy = resolution_strategy
        self.description = description

class PropertyRegistry:
    def __init__(self):
        self._registry: Dict[str, PropertyDefinition] = {}
        self._register_defaults()

    def register(self, definition: PropertyDefinition):
        self._registry[definition.name] = definition

    def get(self, name: str) -> PropertyDefinition:
        # Default fallback for unknown properties
        return self._registry.get(
            name, 
            PropertyDefinition(name=name, stable=False, multi_value=False, expected_type="string", resolution_strategy="recency")
        )

    def _register_defaults(self):
        # Stable single-value facts
        self.register(PropertyDefinition(
            name="birthday",
            stable=True,
            multi_value=False,
            expected_type="date",
            resolution_strategy="dispute",
            description="User's date of birth"
        ))
        self.register(PropertyDefinition(
            name="dog_name",
            stable=True,  # Stable for the specific entity (unless changed)
            multi_value=False,
            expected_type="string",
            resolution_strategy="dispute",
            description="The name of the user's dog"
        ))
        self.register(PropertyDefinition(
            name="family_relation",
            stable=True,
            multi_value=True,  # e.g., sister, father
            expected_type="string",
            resolution_strategy="merge",
            description="Family members and relationships"
        ))

        # Time-varying single-value facts
        self.register(PropertyDefinition(
            name="city",
            stable=False,
            multi_value=False,
            expected_type="string",
            resolution_strategy="recency",
            description="City where the user currently lives"
        ))
        self.register(PropertyDefinition(
            name="employer",
            stable=False,
            multi_value=False,
            expected_type="string",
            resolution_strategy="recency",
            description="User's current employer/company"
        ))
        self.register(PropertyDefinition(
            name="job_title",
            stable=False,
            multi_value=False,
            expected_type="string",
            resolution_strategy="recency",
            description="User's current professional title"
        ))
        self.register(PropertyDefinition(
            name="preference",
            stable=False,
            multi_value=True,  # Multi-value permitted for preferences (e.g. food, music, movie)
            expected_type="string",
            resolution_strategy="recency", # or merge depending on how we model it
            description="User preferences and likes/dislikes"
        ))
        self.register(PropertyDefinition(
            name="hobby",
            stable=False,
            multi_value=True,
            expected_type="string",
            resolution_strategy="merge",
            description="User hobbies and activities"
        ))

registry = PropertyRegistry()
