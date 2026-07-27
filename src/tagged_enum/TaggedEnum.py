from typing import (List, Type, Dict, ForwardRef, Self,
                    Union, Any, get_origin, get_args, ClassVar)
from types import UnionType, NoneType
from enum import Enum, EnumMeta


class TaggedEnumMeta(EnumMeta):
    @property
    def Kind(cls) -> Type[Self]:
        return cls
    
    def __new__(mcls, name: str, bases, namespace: Dict[str, Any], **kw):
        declared: Dict[str, Type[Any]] = {}
        fresh = mcls.__prepare__(name, bases)
        next_case = 0
    
        for k, v in namespace.items():
            if k.startswith('_') or not k.isupper():
                fresh[k] = v
                continue

            if (isinstance(v, type) 
                or get_origin(v) is not None 
                or isinstance(v, str)):
                declared[k] = v
                fresh[k] = next_case
                next_case += 1
            elif v is None:
                declared[k] = NoneType
                fresh[k] = next_case
                next_case += 1
            else:
                fresh[k] = v

        cls = super().__new__(mcls, name, bases, fresh, **kw)

        def sanitize_type(
            t: Type[Any] | ForwardRef | None
        ) -> Type[Any] | str:
            if t is None:
                return NoneType
            
            # Keep self-references as strings instead of ForwardRefs
            if isinstance(t, str) and t == name:
                return name
            
            # Convert ForwardRefs back to strings if they reference self
            if isinstance(t, ForwardRef):
                forward_name = t.__forward_arg__
                if forward_name == name:
                    return name 
                return forward_name
            
            # Handle regular strings (non-self references)
            if isinstance(t, str):
                return t  # Keep as string
            
            origin = get_origin(t)
            if origin is not None:
                args = get_args(t)
                new_args = tuple(sanitize_type(arg) for arg in args)
                
                # Reconstruct the generic type
                if isinstance(t, UnionType):
                    return Union[*new_args]
                else:
                    # For generic types like List, Tuple, etc.
                    return origin[new_args]
            
            # Regular types (int, str, custom classes, etc.)
            return t
        
        sanitized_declared_types = {}
        for member_name, t in declared.items():
            sanitized_types = sanitize_type(t)
            sanitized_declared_types[member_name] = sanitized_types

        cls._declared_types = sanitized_declared_types
        return cls


class TaggedEnum(Enum, metaclass=TaggedEnumMeta):
    """
    Base class for tagged enums with payloads.

    Each uppercase attribute will be considered an **enum case**.
    Each case should be a Python type representing the payload type.
    Collection types are allowed.

    `None` denotes no payload.

    ### Usage:
    ```
    class Message(TaggedEnum):
        PING = None
        STRING = str
        COORDINATES = tuple[int, int]

    ping_msg = Message.PING()
    string_msg = Message.STRING("hello world")
    coords_msg = Message.COORDINATES((1, -1))
    ```
        
    `TaggedEnum`s can be unpacked using `match` statements:
    ```
    match message:
        case Message(case=Message.PING):
            # handle ping
        case Message(case=Message.STRING, item=string):
            # handle string
        case Message(case=Message.COORDINATES, item=(x, y)):
            # handle coords (x, y)
        case _:
            raise ValueError
    ```
    
    The `.kind` property returns the static enum member (the "tag") 
    associated with an instance, allowing for simplified matching 
    when the payload is not required:
    ```
    if message.kind is Message.Kind.STRING:
        print("This is a string message")

    match message.kind:
        case Message.Kind.PING:
            ...
        case Message.Kind.STRING:
            ...
    ```

    ### Members vs. Instances
    **Member**: the static class attribute (e.g., `Message.STRING`) 
    representing the variant's definition, referred to as _case_ or _kind_. 

    **Instance**: the object created by calling a member with a data payload 
    (e.g., `Message.STRING("hello")`). The instance holds a reference to the
    concrete `item` value.

    The `Kind` type attribute serves as a type-level representation of all 
    available members. While an instance contains specific data, its `.kind` 
    and `.case` properties return the member itself, allowing for 
    type-safe dispatching and matching without inspecting the underlying 
    payload.
    """

    Kind: ClassVar[type[Self]]

    def __call__(self, *args, **kwargs) -> Self:
        if not self.is_member:
            raise TypeError
        return self._construct(self, *args, **kwargs)

    @classmethod
    def _construct(cls: Type['TaggedEnum'], 
                   member: 'TaggedEnum', 
                   *args: List[Any]) -> 'TaggedEnum':
        t: Type[Any] = cls._declared_types[member.name]
        arg = args[0] if len(args) > 0 else None
        
        # Type check
        if not cls._typecheck(arg, t):
            raise TypeError(f"{member.name}: expected {t}, got {type(arg)}")
        
        # Create case obj
        inst = object.__new__(cls)
        inst._member_ = member
        inst._name_ = member.name
        inst._value_ = member.value

        inst._item = arg
        inst._case = member
        inst._kind = member

        return inst

    @classmethod
    def make(cls, kind: int, item: Any) -> 'TaggedEnum':
        member = cls(kind)
        return cls._construct(member, item)
    
    # Pattern matching support
    __match_args__ = ("case", "item")

    @classmethod
    def _typecheck(cls, value: Any, typ: Any) -> bool:
        # Handle string forward references - skip validation
        if isinstance(typ, str):
            return True
        
        origin = get_origin(typ)
        args = get_args(typ)
        
        # Handle Union types (including | syntax)
        if origin is Union or origin is UnionType:
            return any(cls._typecheck(value, arg) for arg in args)
        
        # Handle Optional (which is Union[T, None])
        if origin is Union and len(args) == 2 and type(None) in args:
            non_none_type = args[0] if args[1] is type(None) else args[1]
            return value is None or cls._typecheck(value, non_none_type)
        
        # Handle parameterized generics like list[int]
        if origin is not None:
            # Check the container type, skip checking type parameters for now
            return isinstance(value, origin)
        
        # Handle regular types
        if isinstance(typ, type):
            return isinstance(value, typ)
        
        return True
    
    @classmethod
    def item_type(cls, case: int) -> Type[Any]:
        case_name = cls._value2member_map_[case].name
        return cls._declared_types[case_name]

    """ Instance Methods """

    @property
    def case(self) -> 'TaggedEnum':
        return self._case

    @property
    def kind(self) -> Self:
        return self if self.is_member else self._case

    @property
    def item(self) -> Any:
        return self._item

    @property
    def is_member(self) -> bool:
        return not hasattr(self, "_item")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        elif self.value is not other.value:
            return False
        elif self.is_member != other.is_member:
            return False
        elif not self.is_member:
            return self.item == other.item
        else:
            return True

    def __hash__(self) -> int:
        if not self.is_member:
            return hash((self.value, self.item))
        else:
            return hash(self.value)

    def __repr__(self):
        if not self.is_member:
            return f"{self.__class__.__name__}.{self.name}({self.item!r})"
        else:
            return f"{self.__class__.__name__}.{self.name}"
        
    def __str__(self):
        return repr(self)

    # Ensure immutability
    def __setattr__(self, key: str, value: Any):
        if hasattr(self, key):
            raise AttributeError("TaggedEnum instances are immutable")
        super().__setattr__(key, value)
