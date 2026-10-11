// Tactical Battlespace Simulator - runtime module.
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FTBSModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
