// ReSharper disable RedundantUsingDirective
// (these imports are required by CC)
using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Text.RegularExpressions;
using ConnectorLib;
using ConnectorLib.JSON;
using ConnectorLib.SimpleTCP;
using CrowdControl.Common;
using Newtonsoft.Json;
using ConnectorType = CrowdControl.Common.ConnectorType;
using EffectResponse = ConnectorLib.JSON.EffectResponse;
using EffectStatus = CrowdControl.Common.EffectStatus;
using Log = CrowdControl.Common.Log;
using LogLevel = CrowdControl.Common.LogLevel;
using static System.Linq.Enumerable;

namespace CrowdControl.Games.Packs;

[SuppressMessage("Interoperability", "CA1416:Validate platform compatibility")]
public class SuperSmashBrosMeleeESA : SimpleTCPPack<SimpleTCPServerConnector>
{
    public override String Host => "127.0.0.1";
    public override ushort Port => 58432;

    public SuperSmashBrosMeleeESA(UserRecord player, Func<CrowdControlBlock, bool> responseHandler, Action<object> statusUpdateHandler) : base(player, responseHandler, statusUpdateHandler) { }

    public override Game Game => new("Super Smash Bros. Melee (ESA)", "SuperSmashBrosMeleeESA", "GCN", ConnectorType.SimpleTCPServerConnector);
    public override EffectList Effects => new Effect[]
    {
        // Normal Items
        new("Spawn Capsule", "spawnitem_capsule") { Price = 50, Category = "Spawn Item" },
        new("Spawn Box", "spawnitem_box") { Price = 50, Category = "Spawn Item" },
        new("Spawn Barrel", "spawnitem_barrel") { Price = 50, Category = "Spawn Item" },
        new("Spawn Egg", "spawnitem_egg") { Price = 50, Category = "Spawn Item" },
        new("Spawn Party Ball", "spawnitem_party_ball") { Price = 50, Category = "Spawn Item" },
        new("Spawn Barrel Cannon", "spawnitem_barrel_cannon") { Price = 50, Category = "Spawn Item" },
        new("Spawn Bob-omb", "spawnitem_bob_omb") { Price = 50, Category = "Spawn Item" },
        new("Spawn Mr. Saturn", "spawnitem_mr_saturn") { Price = 50, Category = "Spawn Item" },
        new("Spawn Heart Container", "spawnitem_heart_container") { Price = 50, Category = "Spawn Item" },
        new("Spawn Maxim Tomato", "spawnitem_maxim_tomato") { Price = 50, Category = "Spawn Item" },
        new("Spawn Star Man", "spawnitem_star_man") { Price = 50, Category = "Spawn Item" },
        new("Spawn Homerun Bat", "spawnitem_homerun_bat") { Price = 50, Category = "Spawn Item" },
        new("Spawn Beam Sword", "spawnitem_beam_sword") { Price = 50, Category = "Spawn Item" },
        new("Spawn Parasol", "spawnitem_parasol") { Price = 50, Category = "Spawn Item" },
        new("Spawn Green Shell", "spawnitem_green_shell") { Price = 50, Category = "Spawn Item" },
        new("Spawn Red Shell", "spawnitem_red_shell") { Price = 50, Category = "Spawn Item" },
        new("Spawn Ray Gun", "spawnitem_ray_gun") { Price = 50, Category = "Spawn Item" },
        new("Spawn Freezie", "spawnitem_freezie") { Price = 50, Category = "Spawn Item" },
        new("Spawn Food", "spawnitem_food") { Price = 50, Category = "Spawn Item" },
        new("Spawn Proxy Mine", "spawnitem_proxy_mine") { Price = 50, Category = "Spawn Item" },
        new("Spawn Flipper", "spawnitem_flipper") { Price = 50, Category = "Spawn Item" },
        new("Spawn Super Scope", "spawnitem_super_scope") { Price = 50, Category = "Spawn Item" },
        new("Spawn Star Rod", "spawnitem_star_rod") { Price = 50, Category = "Spawn Item" },
        new("Spawn Lips Stick", "spawnitem_lips_stick") { Price = 50, Category = "Spawn Item" },
        new("Spawn Fan", "spawnitem_fan") { Price = 50, Category = "Spawn Item" },
        new("Spawn Fire Flower", "spawnitem_fire_flower") { Price = 50, Category = "Spawn Item" },
        new("Spawn Super Mushroom", "spawnitem_super_mushroom") { Price = 50, Category = "Spawn Item" },
        new("Spawn Mini Mushroom", "spawnitem_mini_mushroom") { Price = 50, Category = "Spawn Item" },
        new("Spawn Hammer", "spawnitem_hammer") { Price = 50, Category = "Spawn Item" },
        new("Spawn Warp Star", "spawnitem_warp_star") { Price = 50, Category = "Spawn Item" },
        new("Spawn Screw Attack", "spawnitem_screw_attack") { Price = 50, Category = "Spawn Item" },
        new("Spawn Bunny Hood", "spawnitem_bunny_hood") { Price = 50, Category = "Spawn Item" },
        new("Spawn Metal Box", "spawnitem_metal_box") { Price = 50, Category = "Spawn Item" },
        new("Spawn Cloaking Device", "spawnitem_cloaking_device") { Price = 50, Category = "Spawn Item" },
        new("Spawn Pokeball", "spawnitem_pokeball") { Price = 50, Category = "Spawn Item" },
        // Special Items
        new("Spawn Yoshi Egg", "spawnitem_yoshi_egg") { Price = 50, Category = "Spawn Item" },
        new("Spawn Goomba", "spawnitem_goomba") { Price = 50, Category = "Spawn Item" },
        new("Spawn Redead", "spawnitem_redead") { Price = 50, Category = "Spawn Item" },
        new("Spawn Octorok", "spawnitem_octorok") { Price = 50, Category = "Spawn Item" },
        new("Spawn Ottosea", "spawnitem_ottosea") { Price = 50, Category = "Spawn Item" },
        new("Spawn Stone", "spawnitem_stone") { Price = 50, Category = "Spawn Item" },
    };
}
