#include "TBSGameState.h"

#include "Net/UnrealNetwork.h"

void ATBSGameState::GetLifetimeReplicatedProps(TLifetimeProperties& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ATBSGameState, SessionPhase);
}
