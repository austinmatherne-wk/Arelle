"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from abc import ABC
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Self

from arelle.ModelValue import AnyURI, DateTime, IsoDuration, QName
from arelle.PythonUtil import FrozenDict, FrozenOrderedSet


class PeriodType(Enum):
    """
    Defines the period values that can be used on taxonomy model concept objects.
    """

    DURATION = "duration"
    INSTANT = "instant"
    NONE = "none"


class TypedSort(Enum):
    """
    Defines the typed sort values that can be used on taxonomy model dimension objects.
    """

    ASC = "asc"
    DESC = "desc"


class Cycles(Enum):
    """
    Defines the cycles that can be used on taxonomy model relationship type objects.
    """

    ANY = "any"
    NONE = "none"
    UNDIRECTED = "undirected"


class TotalLocation(Enum):
    """
    Defines the total location values that can be used on taxonomy model axis dimension objects.
    """

    START = "start"
    END = "end"

class PeriodAlign(Enum):
    """
    Defines the period alignment values that can be used on taxonomy model axis dimension objects.
    """

    START = "@start"
    END = "@end"

@dataclass(frozen=True)
class PeriodFormat:
    """
    Defines a duration of time with an end date as defined by the xBRL-CSV spec.
    https://www.xbrl.org/Specification/xbrl-csv/REC-2021-10-13+errata-2023-04-19/xbrl-csv-REC-2021-10-13+corrected-errata-2023-04-19.html#sec-period-formats
    """

    value: str

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class CSVDimensionsObject:
    """
    Defines the dimensions object as defined in the xBRL-CSV spec.
    """
    concept: str
    entity: str
    unit: str
    language: str
    properties: dict[QName, Any]

    def __getitem__(self, key: QName) -> Any:
        return self.properties[key]

@dataclass(frozen=True)
class TaxonomyModelObject(ABC):
    """
    The base class for all taxonomy model objects.
    This class should not be instantiated directly.
    """

    referenceable: ClassVar[bool]

    def __new__(cls: type[Self], *args: Any, **kwargs: Any) -> Self:
        if cls is TaxonomyModelObject:
            raise TypeError(f"Cannot instantiate abstract class {cls.__name__}")
        return super().__new__(cls)


@dataclass(frozen=True)
class PropertyObject(TaxonomyModelObject):
    """
    Defines property values for objects in the taxonomy.
    """

    referenceable: ClassVar[bool] = False

    property: QName
    value: Any


@dataclass(frozen=True)
class TransformObject(TaxonomyModelObject):
    """
    Defines a transform object in the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    input_data_type: QName
    output_data_type: QName


@dataclass(frozen=True)
class AxisDimensionObject(TaxonomyModelObject):
    """
    Defines the dimensions associated with an axis in the data table object.
    """

    referenceable: ClassVar[bool] = False

    dimension_name: QName
    show_total: bool | None
    show_ancestor_columns: FrozenOrderedSet[str] | None
    total_location: TotalLocation | None
    period_align: FrozenOrderedSet[PeriodAlign] | None


@dataclass(frozen=True)
class AxisObject(TaxonomyModelObject):
    """
    Defines the dimensions associated with an axis and the labels and order that items appear on the axis.
    """

    referenceable: ClassVar[bool] = False


@dataclass(frozen=True)
class DataTableObject(TaxonomyModelObject):
    """
    Defines a two dimensional structure based on the structure of a cube.
    """

    referenceable: ClassVar[bool] = True


@dataclass(frozen=True)
class TableTemplateObject(TaxonomyModelObject):
    """
    Defines a two dimensional structure where facts can be allocated to for presentation purposes.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    row_id_column: str | None
    dimensions: CSVDimensionsObject
    decimals: Decimal | None

@dataclass(frozen=True)
class RequiredCubeRelationshipObject(TaxonomyModelObject):
    """
    Defines a required relationship for a cube type.
    """

    referenceable: ClassVar[bool] = False

    relationship_type_name: QName
    source: QName | None
    target: QName | None

@dataclass(frozen=True)
class AllowedCubeDimensionObject(TaxonomyModelObject):
    """
    Defines the allowed dimensions for a cube.
    """

    referenceable: ClassVar[bool] = False

    dimension_name: QName | None
    dimension_type: str | None
    dimension_data_type: QName | None
    required: bool | None


@dataclass(frozen=True)
class CubeTypeObject(TaxonomyModelObject):
    """
    Used to define the allowable dimensions associated with different cube types.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    base_cube_type: QName | None
    period_dimension: bool | None
    entity_dimension: bool | None
    unit_dimension: bool | None
    taxonomy_defined_dimension: bool | None
    allowed_cube_dimensions: FrozenOrderedSet[AllowedCubeDimensionObject] | None
    required_cube_relationships: FrozenOrderedSet[RequiredCubeRelationshipObject] | None


@dataclass(frozen=True)
class ReferenceTypeObject(TaxonomyModelObject):
    """
    Used to define a reference type in the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    uri: AnyURI | None
    allowed_objects: FrozenOrderedSet[QName] | None
    ordered_properties: FrozenOrderedSet[QName] | None
    require_properties: FrozenOrderedSet[QName] | None


@dataclass(frozen=True)
class LabelTypeObject(TaxonomyModelObject):
    """
    Used to define a label type in the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    uri: AnyURI | None
    data_type: QName | None
    allowed_objects: FrozenOrderedSet[QName] | None


@dataclass(frozen=True)
class ReferenceObject(TaxonomyModelObject):
    """
    Defines references within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName | None
    extend_target_name: QName | None
    related_names: FrozenOrderedSet[QName] | None
    reference_type: QName
    language: str | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class LabelObject(TaxonomyModelObject):
    """
    Defines labels within the taxonomy.
    """

    referenceable: ClassVar[bool] = False

    related_name: QName
    label_type: QName
    language: str
    value: str
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class UnitTypeObject(TaxonomyModelObject):
    """
    Associates multiple datatypes used in a unit to a base datatype.
    """

    referenceable: ClassVar[bool] = False

    data_type_numerator: QName | None
    data_type_denominator: QName | None
    data_type_multiplier: QName | None


@dataclass(frozen=True)
class DataTypeObject(TaxonomyModelObject):
    """
    Defines datatypes within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    base_type: QName
    enumeration: FrozenOrderedSet[Any] | None
    min_inclusive: Decimal | None
    max_inclusive: Decimal | None
    min_exclusive: Decimal | None
    max_exclusive: Decimal | None
    total_digits: int | None
    fraction_digits: int | None
    length: int | None
    min_length: int | None
    max_length: int | None
    white_space: str | None
    patterns: FrozenOrderedSet[str] | None
    unit_types: UnitTypeObject | None


@dataclass(frozen=True)
class PropertyTypeObject(TaxonomyModelObject):
    """
    Used to define properties that can be used on other taxonomy objects such as concepts and relationships.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    data_type: QName
    enumeration_domain: QName | None
    definitional: bool | None
    allowed_objects: FrozenOrderedSet[QName] | None
    allowed_as_link_property: bool | None


@dataclass(frozen=True)
class RelationshipTypeObject(TaxonomyModelObject):
    """
    Used to define properties of a relationship.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    uri: AnyURI | None
    cycles: Cycles
    allowed_link_properties: FrozenOrderedSet[QName] | None
    required_link_properties: FrozenOrderedSet[QName] | None
    source_objects: FrozenOrderedSet[QName] | None
    target_objects: FrozenOrderedSet[QName] | None


@dataclass(frozen=True)
class RelationshipObject(TaxonomyModelObject):
    """
    Allows the assignment of relationships to another taxonomy object that contains relationships,
    such as adding a domain member to a domain object.
    It defines relationships between concepts, such as summation-item and parent-child.
    """

    referenceable: ClassVar[bool] = False

    source: QName
    target: QName
    order: int | None
    weight: int | None
    preferred_label: QName | None
    usable: bool | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class NetworkObject(TaxonomyModelObject):
    """
    Defines networks within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName | None
    relationship_type_name: QName | None
    roots: FrozenOrderedSet[QName] | None
    relationships: FrozenOrderedSet[RelationshipObject] | None
    extend_target_name: QName | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class GroupContentObject(TaxonomyModelObject):
    """
    Links groups within the taxonomy to taxonomy objects.
    """

    referenceable: ClassVar[bool] = False

    group_name: AnyURI
    related_names: FrozenOrderedSet[NetworkObject]


@dataclass(frozen=True)
class GroupObject(TaxonomyModelObject):
    """
    Defines groups within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    group_uri: AnyURI | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class UnitObject(TaxonomyModelObject):
    """
    Defines a unit object in the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    data_type: QName
    data_type_numerator: QName | None
    data_type_denominator: QName | None


@dataclass(frozen=True)
class EntityObject(TaxonomyModelObject):
    """
    Defines an entity object in the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class DateResolutionObject(TaxonomyModelObject):
    """
    Defines dates that are used by the period constraint object.
    """

    referenceable: ClassVar[bool] = False

    concept_name: QName | None
    context: str | None
    value: DateTime | None
    time_shift: IsoDuration | None


@dataclass(frozen=True)
class PeriodConstraintObject(TaxonomyModelObject):
    """
    Defines periods that can be used on the period dimension.
    """

    referenceable: ClassVar[bool] = False

    period_type: PeriodType
    time_span: IsoDuration | None
    period_format: PeriodFormat | None
    month_day: DateResolutionObject | None
    end_date: DateResolutionObject | None
    start_date: DateResolutionObject | None
    on_or_after: DateResolutionObject | None
    on_or_before: DateResolutionObject | None


@dataclass(frozen=True)
class CubeDimensionObject(TaxonomyModelObject):
    """
    Defines dimensions within the cube object.
    """

    referenceable: ClassVar[bool] = False

    dimension_name: QName
    domain_name: QName | None
    typed_sort: TypedSort | None
    allow_domain_facts: bool | None
    period_constraints: FrozenOrderedSet[PeriodConstraintObject] | None


@dataclass(frozen=True)
class CubeObject(TaxonomyModelObject):
    """
    Defines a multidimensional structure to organize facts.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    cube_type: QName | None
    cube_dimensions: FrozenOrderedSet[CubeDimensionObject]
    cube_networks: FrozenOrderedSet[NetworkObject] | None
    exclude_cubes: FrozenOrderedSet[QName] | None
    cube_complete: bool | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class DomainRootObject(TaxonomyModelObject):
    """
    Defines the domain root objects within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class DomainObject(TaxonomyModelObject):
    """
    Defines domains within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName | None
    root: QName | None
    relationships: FrozenOrderedSet[RelationshipObject] | None
    extendTargetName: QName | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class DimensionObject(TaxonomyModelObject):
    """
    Defines dimensions within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    domain_data_type: QName | None
    domain_name: QName | None
    cube_types: FrozenOrderedSet[QName] | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class MemberObject(TaxonomyModelObject):
    """
    Defines members within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class AbstractObject(TaxonomyModelObject):
    """
    Defines abstracts within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class ConceptObject(TaxonomyModelObject):
    """
    Defines concepts within the taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    data_type: QName
    period_type: PeriodType
    enumeration_domain: QName | None
    nillable: bool | None
    properties: FrozenOrderedSet[PropertyObject] | None


@dataclass(frozen=True)
class ImportTaxonomyObject(TaxonomyModelObject):
    """
    Defines external taxonomy objects that can be imported into the taxonomy.
    """

    referenceable: ClassVar[bool] = False

    taxonomy_name: QName
    include_objects: FrozenOrderedSet[QName] | None
    include_object_types: FrozenOrderedSet[QName] | None
    exclude_labels: bool | None
    follow_imports: bool | None


@dataclass(frozen=True)
class TaxonomyObject(TaxonomyModelObject):
    """
    Defines all objects and properties of a taxonomy.
    """

    referenceable: ClassVar[bool] = True

    name: QName
    framework_name: str | None
    version: str | None
    resolved: bool
    imported_taxonomies: FrozenOrderedSet[ImportTaxonomyObject] | None
    abstracts: FrozenOrderedSet[AbstractObject] | None
    concepts: FrozenOrderedSet[ConceptObject] | None
    cubes: FrozenOrderedSet[CubeObject] | None
    cube_types: FrozenOrderedSet[CubeTypeObject] | None
    data_types: FrozenOrderedSet[DataTypeObject] | None
    dimensions: FrozenOrderedSet[DimensionObject] | None
    domains: FrozenOrderedSet[DomainObject] | None
    domain_roots: FrozenOrderedSet[DomainRootObject] | None
    entities: FrozenOrderedSet[EntityObject] | None
    groups: FrozenOrderedSet[GroupObject] | None
    group_contents: FrozenOrderedSet[GroupContentObject] | None
    labels: FrozenOrderedSet[LabelObject] | None
    members: FrozenOrderedSet[MemberObject] | None
    networks: FrozenOrderedSet[NetworkObject] | None
    property_types: FrozenOrderedSet[PropertyTypeObject] | None
    references: FrozenOrderedSet[ReferenceObject] | None
    reference_types: FrozenOrderedSet[ReferenceTypeObject] | None
    relationship_types: FrozenOrderedSet[RelationshipTypeObject] | None
    table_templates: FrozenOrderedSet[TableTemplateObject] | None
    data_tables: FrozenOrderedSet[DataTableObject] | None
    units: FrozenOrderedSet[UnitObject] | None
    properties: FrozenOrderedSet[PropertyObject] | None
    transforms: FrozenOrderedSet[TransformObject] | None


@dataclass(frozen=True)
class URLMappingObject(TaxonomyModelObject, Mapping[str, AnyURI]):
    """
    Defines namespace prefix and associated URL.
    """

    referenceable: ClassVar[bool] = False

    _url_mapping: FrozenDict[str, AnyURI]

    def __getitem__(self, key: str) -> AnyURI:
        return self._url_mapping[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._url_mapping)

    def __len__(self) -> int:
        return len(self._url_mapping)


@dataclass(frozen=True)
class NamespaceObject(TaxonomyModelObject, Mapping[str, AnyURI]):
    """
    Defines the namespaces used in the taxonomy.
    """

    referenceable: ClassVar[bool] = False

    _namespaces: FrozenDict[str, AnyURI]

    def __getitem__(self, key: str) -> AnyURI:
        return self._namespaces[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._namespaces)

    def __len__(self) -> int:
        return len(self._namespaces)


@dataclass(frozen=True)
class DocumentInfoObject(TaxonomyModelObject):
    """
    Defines the document information for a taxonomy.
    """

    referenceable: ClassVar[bool] = False

    document_type: AnyURI
    namespaces: NamespaceObject
    document_namespace: str
    url_mapping: URLMappingObject | None


@dataclass(frozen=True)
class TaxonomyModule(TaxonomyModelObject):
    """
    Defines the container of a taxonomy, including all objects and document information.
    """

    referenceable: ClassVar[bool] = False

    document_info: DocumentInfoObject
    taxonomy: TaxonomyObject
