// Replicated session state visible to all clients (map state, session phase).
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "TBSGameState.generated.h"

UENUM(BlueprintType)
enum class ETBSSessionPhase : uint8
{
    Lobby,
    Running,
    Paused,
    Ended
};

UCLASS()
class TBS_API ATBSGameState : public AGameStateBase
{
    GENERATED_BODY()

public:
    UPROPERTY(Replicated, BlueprintReadOnly, Category = "TBS")
    ETBSSessionPhase SessionPhase = ETBSSessionPhase::Lobby;

    virtual void GetLifetimeReplicatedProps(TLifetimeProperties& OutLifetimeProps) const override;
};
