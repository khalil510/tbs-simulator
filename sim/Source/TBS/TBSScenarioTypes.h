// Data structures mirroring schemas/scenario.schema.json (the canonical
// contract with the Django backend). Keep in lockstep with the schema -
// any field change here is a schema change first.
#pragma once

#include "CoreMinimal.h"
#include "TBSScenarioTypes.generated.h"

UENUM(BlueprintType)
enum class ETBSSide : uint8
{
    Blue,
    Red,
    Green,
    Neutral
};

UENUM(BlueprintType)
enum class ETBSEntityKind : uint8
{
    InfantrySoldier,
    InfantrySquad,
    Team,
    SpawnPoint,
    Marker
};

USTRUCT(BlueprintType)
struct TBS_API FTBSWaypoint
{
    GENERATED_BODY()

    UPROPERTY() double Lat = 0.0;
    UPROPERTY() double Lon = 0.0;
    UPROPERTY() double Alt = 0.0;
    UPROPERTY() float SpeedMs = 1.4f;
    UPROPERTY() FString Action = TEXT("move"); // move|jog|overwatch|hold|engage
};

USTRUCT(BlueprintType)
struct TBS_API FTBSEntityDef
{
    GENERATED_BODY()

    UPROPERTY() FString Id;          // e.g. "ent-1"
    UPROPERTY() ETBSEntityKind Kind = ETBSEntityKind::InfantrySquad;
    UPROPERTY() ETBSSide Side = ETBSSide::Blue;
    UPROPERTY() double Lat = 0.0;
    UPROPERTY() double Lon = 0.0;
    UPROPERTY() float AltMeters = 0.0f;
    UPROPERTY() float HeadingDeg = 0.0f;
    UPROPERTY() int32 SoldierCount = 9;
    UPROPERTY() FString Loadout = TEXT("standard-rifle");
    UPROPERTY() TArray<FTBSWaypoint> Waypoints;
};

USTRUCT(BlueprintType)
struct TBS_API FTBSObjectiveDef
{
    GENERATED_BODY()

    UPROPERTY() FString Id;          // e.g. "obj-1"
    UPROPERTY() FString Description;
    UPROPERTY() int32 Points = 0;
    UPROPERTY() FString TriggerType; // area-clear|reach-area|time-limit|eliminate-entity
    UPROPERTY() float TriggerRadiusMeters = 0.0f;
};

USTRUCT(BlueprintType)
struct TBS_API FTBSScenario
{
    GENERATED_BODY()

    UPROPERTY() FString SchemaVersion;
    UPROPERTY() FString Name;
    UPROPERTY() FDateTime CreatedAt;
    UPROPERTY() TArray<double> BBox; // [minLon, minLat, maxLon, maxLat] WGS84
    UPROPERTY() FString TerrainProvider; // cesium-ion|wmts|local-tiles
    UPROPERTY() int32 CesiumAssetId = INDEX_NONE;
    UPROPERTY() FString TimeOfDay = TEXT("12:00");
    UPROPERTY() FString Weather = TEXT("clear");
    UPROPERTY() float FogDensity = 0.0f;
    UPROPERTY() TArray<FTBSEntityDef> Entities;
    UPROPERTY() TArray<FTBSObjectiveDef> Objectives;

    bool IsValid(FString& OutError) const;
};

USTRUCT(BlueprintType)
struct TBS_API FTBSSessionHandoff
{
    GENERATED_BODY()

    UPROPERTY() FString Ticket;            // short-lived JWT from Django
    UPROPERTY() FString SessionId;
    UPROPERTY() FString ScenarioExportUrl; // absolute URL on the API host
    UPROPERTY() int32 ExpiresInSeconds = 60;
};
