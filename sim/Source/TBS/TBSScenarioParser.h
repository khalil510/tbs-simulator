// Parses the canonical scenario JSON (schemas/scenario.schema.json) that the
// Django backend serves at /api/scenarios/{id}/export/.
#pragma once

#include "CoreMinimal.h"
#include "TBSScenarioTypes.h"

class TBS_API FTBSScenarioParser
{
public:
    /** Parse scenario JSON. On failure returns false and sets OutError. */
    static bool Parse(const FString& JsonBody, FTBSScenario& OutScenario, FString& OutError);
};
