#include "TBSGameMode.h"

#include "Engine/World.h"
#include "TBSScenarioParser.h"
#include "TBSSessionClient.h"

ATBSGameMode::ATBSGameMode()
{
    // Pawn classes are wired in Blueprint subclasses in later milestones.
}

void ATBSGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (HasAuthority())
    {
        FString Error;
        if (!FTBSSessionClient::LoadHandoffFromCommandLine(Handoff, Error))
        {
            UE_LOG(LogTemp, Error, TEXT("[TBS] session handoff failed: %s"), *Error);
            return;
        }
        FTBSSessionClient::FetchScenario(
            Handoff, FTBSScenarioLoaded::CreateUObject(this, &ATBSGameMode::OnScenarioLoaded));
    }
}

void ATBSGameMode::OnScenarioLoaded(bool bSuccess, const FTBSScenario& InScenario)
{
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("[TBS] could not load scenario for session %s"), *Handoff.SessionId);
        return;
    }
    Scenario = InScenario;
    UE_LOG(LogTemp, Log, TEXT("[TBS] loaded scenario '%s' (%d entities, %d objectives)"),
           *Scenario.Name, Scenario.Entities.Num(), Scenario.Objectives.Num());
    SpawnScenarioEntities();
    // TODO(M4): report state=running back to Django so the instructor UI
    // shows the session as live.
}

void ATBSGameMode::SpawnScenarioEntities()
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }
    for (const FTBSEntityDef& Entity : Scenario.Entities)
    {
        // TODO(M3): spawn soldier/squad pawns at the georeferenced position.
        // Coordinate conversion goes through the Cesium georeference anchor
        // (see docs/architecture.md - WGS84 <-> UE conversion is milestone M2).
        UE_LOG(LogTemp, Log, TEXT("[TBS] would spawn %s (%d soldiers, side %d) at %.6f,%.6f"),
               *Entity.Id, Entity.SoldierCount, static_cast<int32>(Entity.Side), Entity.Lat, Entity.Lon);
    }
}
