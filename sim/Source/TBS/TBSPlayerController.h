// Trainee player controller. Instructor extensions (pause/inject/spectate)
// land in a subclass during milestone M5.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "TBSPlayerController.generated.h"

UCLASS()
class TBS_API ATBSPlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    ATBSPlayerController();
};
