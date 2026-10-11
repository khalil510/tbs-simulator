using UnrealBuildTool;

public class TBS : ModuleRules
{
    public TBS(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput",
            "AIModule",
            "GameplayTasks",
            "Http",
            "Json",
            "JsonUtilities"
        });
    }
}
