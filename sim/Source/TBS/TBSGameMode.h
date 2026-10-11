// Server-side game mode. On BeginPlay it performs the session handoff,
// loads the scenario, and spawns entities.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "TBSScenarioTypes.h"
#include "TBSGameMode.generated.h"

UCLASS()
class TBS_API ATBSGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ATBSGameMode();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "TBS")
    const FTBSScenario& GetScenario() const { return Scenario; }

protected:
    /** Callback for the async scenario fetch (session handoff step 2). */
    void OnScenarioLoaded(bool bSuccess, const FTBSScenario& InScenario);

    /** Spawn pawns/AI for every entity in the loaded scenario. */
    void SpawnScenarioEntities();

    UPROPERTY()
    FTBSScenario Scenario;

    FTBSSessionHandoff Handoff;
};
