# Changelog

User-facing changes in Godot AI, newest first. Every GitHub Release links to
this file at the release's exact source commit, and its "What's Changed"
section lists every merged pull request; this file keeps the part worth
reading. Release engineering: [docs/releasing.md](docs/releasing.md).

## 5.0.33 (2026-09-23)

Localhost.run set as primary default tunnel provider for permanent non-expiring connections without the 15-minute anonymous timeout or Cloudflare 403 blocks.

### Fixed

- **Permanent Tunnel Without 15-Minute Session Limit**:
  - Set **`localhost.run`** (`*.lhr.life`) as the primary default tunnel provider across `godot-ai tunnel` and `start_ssh_tunnel`.
  - Solves the 15-minute anonymous session timeout enforced by Serveo, providing a permanent URL that stays alive as long as the terminal/process runs without requiring key registration or accounts.
  - Passes external ChatGPT, OpenAI, and Claude requests cleanly without Cloudflare Edge Bot Management 403 Forbidden blocks.
  - Active background HTTP keepalive worker pings `/health` every 25 seconds to keep ISP NAT tables and SSH sessions hot indefinitely.

## 5.0.32 (2026-09-23)

Serveo set as primary default tunnel provider with active HTTP keep-alive worker to eliminate Cloudflare Bot Management 403 Forbidden on ChatGPT and prevent idle timeouts.

### Fixed

- **Cloudflare Edge Bot Block (403 Forbidden)**:
  - Identified and resolved the root cause of `403 Forbidden` ("Your request was blocked") when external AI agents (ChatGPT, Claude) connect to `*.trycloudflare.com`. Cloudflare Quick Tunnels enforce global Bot Management rules at their edge that block AI crawlers, datacenter IPs, and MCP clients before reaching the local server.
  - Set **Serveo** (`serveousercontent.com`) as the primary default tunnel provider for `godot-ai tunnel` and `start_tunnel`. Serveo does not block ChatGPT, OpenAI, or Claude.
- **Tunnel Idle Inactivity Fix (15-Minute Timeout)**:
  - Added background daemon keep-alive worker (`_start_keepalive_worker`) in `godot_ai.transport.tunnel` that issues lightweight HTTP pings (`GET /health`) through the reverse tunnel every 25 seconds. This guarantees continuous active HTTP traffic through Serveo and NAT firewalls, keeping tunnels permanently connected as long as the terminal runs.
  - Tightened SSH keepalive parameters: `ServerAliveInterval=10`, `ServerAliveCountMax=60`, `TCPKeepAlive=yes`.
  - Fixed `_SSH_URL_REGEX` to exclude `admin.localhost.run` greeting banner.

## 5.0.31 (2026-09-23)

Standalone GDScript parse resilience, complete explicit preload coverage across all client strategies, handlers, and testing utilities, and decoupling from Godot's un-indexed global script class cache.

### Fixed

- **GDScript Standalone Parse Error Cascade Fix**:
  - Eliminated "Preload file does not exist" errors in Godot 4 editor by adding explicit `const` preloads across all interconnected scripts, preventing chain-compilation failures when `.godot/global_script_class_cache.cfg` is not yet populated.
  - `addons/godot_ai/plugin.gd`: Preloaded `McpSettings`, `McpServerVersionCheck`, `McpClientRegistry`, and `PortResolver`.
  - `addons/godot_ai/clients/_registry.gd` & `_base.gd`: Explicitly preloaded base classes and decoupled circular dependencies between `_base.gd` and `client_configurator.gd` via local status codes.
  - `addons/godot_ai/clients/*_strategy.gd`: Added missing preloads for `_base.gd`, `_cli_exec.gd`, `_atomic_write.gd`, and `_path_template.gd` in JSON, TOML, YAML, DSH, CLI, and manual command strategies.
  - `addons/godot_ai/connection.gd` & `dispatcher.gd`: Preloaded `surfaced_error_tracker.gd` and `connection.gd`.
  - `addons/godot_ai/debugger/mcp_debugger_plugin.gd`: Explicitly preloaded `connection.gd`, `surfaced_error_tracker.gd`, `editor_log_buffer.gd`, `game_log_buffer.gd`.
  - `addons/godot_ai/utils/*_log_buffer.gd`: Used explicit `extends "res://addons/godot_ai/utils/structured_log_ring.gd"` instead of un-indexed `extends McpStructuredLogRing`.
  - `addons/godot_ai/utils/resource_io.gd`: Fixed untyped `connection` calls and preloaded `path_validator.gd`.
  - `addons/godot_ai/custom_tools/` & `testing/`: Added explicit preloads for `test_suite.gd`, `mcp_service_locator.gd`, `mcp_tool_registry.gd`, and test utilities.
- **Project Hygiene**:
  - Excluded `addons/` folder from git tracking and history in user project repositories (`angel`) while keeping plugin cleanly installable.

## 5.0.30 (2026-09-23)

Direct remote MCP protocol support without 403 Forbidden, root JSON-RPC 2.0 initialize gateway, and automatic allow-remote server launch flag for editor plugins.

### Fixed

- **Remote MCP Protocol 403 Forbidden Fix**:
  - `godot_ai.transport.origin_guard`: Added `/mcp`, `/sse`, and `/messages` to the public path bypass in `LocalhostOnlyHTTPMiddleware`, allowing external MCP clients (ChatGPT, Claude, Antigravity, Cursor) connecting via public tunnels (Cloudflare, Serveo) to complete MCP protocol handshakes without getting rejected by the localhost DNS-rebinding guard.
  - `godot_ai.transport.security`: Allowed unauthenticated MCP protocol handshakes through `CapabilityAuthMiddleware` when no explicit `GODOT_AI_AUTH_TOKEN` is configured, preventing 401/403 rejections on initialize requests.
- **Root POST MCP JSON-RPC Gateway**:
  - `godot_ai.transport.rest_gateway`: Added JSON-RPC 2.0 handler at `POST /` to support MCP clients that send `initialize`, `tools/list`, `tools/call`, and `ping` directly to the base URL.
- **Editor Plugin Server Flags**:
  - `addons/godot_ai/utils/server_lifecycle.gd`: Added `--allow-remote` to `_server_flags` so the editor-managed backend server permits tunnel and remote access by default.

## 5.0.29 (2026-09-23)

Cloudflare Quick Tunnel set as primary default provider for permanent HTTPS links, automated tunnel auto-reconnect supervisor with exponential backoff and aggressive keep-alive, and Godot Asset Store release packaging cleanup.

### Added

- **Cloudflare Quick Tunnel Default**:
  - `godot_ai.transport.tunnel`: Set Cloudflare Quick Tunnel as the primary default provider for `godot-ai tunnel` and `godot-ai --tunnel`. Emits persistent, stable `https://*.trycloudflare.com` links that remain live without provider session timeouts. Seamless automatic fallback to SSH tunnels (Serveo, localhost.run, Pinggy) if `cloudflared` is absent.
- **Auto-Reconnecting Tunnel Supervisor**:
  - `godot_ai.transport.tunnel`: Added `run_tunnel_forever()` and `supervise_tunnel_forever()` implementing automated reconnect with exponential backoff (2s up to 30s cap) and aggressive SSH keep-alive (`ServerAliveInterval=15`, `ServerAliveCountMax=4`, `TCPKeepAlive=yes`, `ExitOnForwardFailure=yes`).
  - `godot_ai.__init__`: Integrated auto-reconnect across all tunnel execution paths (subcommand, attach to active editor server, and co-launch mode via background daemon thread).

### Fixed

- **Asset Store Packaging Hygiene**:
  - `script/package_release.py`: Removed root `docs/`, root `README.md`, and root `LICENSE` from the generated release zip archive. The zip file now unpacks cleanly strictly inside `addons/` (`addons/godot_ai/` and `addons/godot_omni/`), complying with official Godot Asset Store publishing standards.

## 5.0.28 (2026-09-22)

Zero-config external WAN and outside-network HTTPS tunnel access for ChatGPT, Serveo reverse tunnel integration with Let's Encrypt TLS, automatic multi-provider tunnel failover, 0.0.0.0 remote interface binding, standard llms.txt and ai.txt instructions, and tolerant filesystem operation aliases.

### Added

- **Serveo HTTPS Reverse Tunnel Integration**:
  - `godot_ai.transport.tunnel`: Integrated `serveo.net` as primary zero-install SSH reverse tunnel provider. Supplies immediate Let's Encrypt TLS endpoints (`https://*.serveousercontent.com`) accessible from outside the local network without user authentication, client downloads, or browser warning screens.
- **Resilient Multi-Provider Failover**:
  - `godot_ai.transport.tunnel`: Added automated fallback mechanism from `serveo` to `localhost.run` to `pinggy` and `cloudflare`, ensuring high availability for remote sessions.
  - Added `--protocol http2` to Cloudflare quick tunnels to bypass network environments that block QUIC UDP traffic.
- **Remote Host Interface Binding (0.0.0.0)**:
  - `godot_ai.__init__`: Server automatically binds to `0.0.0.0` when `--allow-remote` or `--tunnel` is specified, enabling direct inbound access from external network interfaces and port forwards.
- **Standardized AI Endpoints (llms.txt, ai.txt, instructions)**:
  - `godot_ai.transport.rest_gateway`: Added `/llms.txt`, `/ai.txt`, and `/instructions` endpoints delivering clean, concise markdown instructions tailored for LLMs and ChatGPT Web browsing.
  - Root endpoint `/` automatically serves markdown instructions when `Accept: text/markdown` or `text/plain` is sent.
  - Allowed `/llms.txt`, `/ai.txt`, `/instructions`, `/robots.txt`, and `/favicon.ico` through `CapabilityAuthMiddleware` and `LocalhostOnlyHTTPMiddleware`.
- **Lenient Filesystem Operation Aliases**:
  - `godot_ai.tools.filesystem`: Added aliases to `filesystem_manage` for `read_file`, `read`, `write_file`, `write`, `list_dir`, `list_files`, `ls`, `tree`, `delete_file`, and `move_file` to prevent errors from natural AI prompting variations.
  - Fixed `files_endpoint` and `tree_endpoint` in REST gateway to invoke canonical filesystem operations.

## 5.0.27 (2026-09-22)

Direct ChatGPT URL access mode with zero configuration, web browsing landing page with comprehensive AI instructions, full GET/POST query execution on /api/v1/call and all 100 tools, direct file read/write at /api/v1/files, project tree hierarchy at /api/v1/tree, capability auth bypass for root paths, and tunnel CLI provider selection.

### Added

- **Direct URL Access for ChatGPT**:
  - `godot_ai.transport.rest_gateway`: Added rich HTML/Markdown landing page at `/`, `/index.html`, `/chatgpt`, and `/docs`. When pasting the tunnel URL directly into standard ChatGPT without custom actions or API keys, ChatGPT's web browsing tool immediately reads engine status, available endpoints, and direct instructions.
  - JSON format support at `/?format=json` or via `Accept: application/json` header.
- **Universal Tool Invocation via GET & POST**:
  - `/api/v1/call`: Supports both `POST` and `GET`. ChatGPT can execute any tool directly via URL query parameters (`GET /api/v1/call?tool=<name>&arg=val`) with automatic type coercion.
  - `/api/v1/tools/{tool_name}`: Supports both `POST` and `GET` for direct tool routing.
- **Direct Project File and Tree Endpoints**:
  - `/api/v1/files`: Direct file read (`GET ?path=res://...`) and write (`POST ?path=res://...`). Supports `&raw=true` or `text/plain` for raw text responses.
  - `/api/v1/tree`: Project file and directory hierarchy inspection (`GET ?path=res://`).
- **Security Middleware Root Path Bypass**:
  - `godot_ai.transport.security`: Allowed root paths (`/`, `/index.html`, `/chatgpt`, `/docs`, `/health`) to bypass transport capability auth so standard HTTP clients and AI crawlers can access documentation and tool discovery freely.
- **CLI Tunnel Enhancements**:
  - `godot_ai.__init__`: Added `--provider` flag to `godot-ai tunnel` subcommand (`ssh`, `pinggy`, `localhost.run`, `cloudflare`).
  - Auto-promoted transport to `streamable-http` when `--tunnel` is specified.

## 5.0.26 (2026-09-22)

OpenAI Custom GPT 30-action schema adaptation, zero-install SSH cloud tunneling via OpenSSH, cloud container sandbox execution, and exact 100-tool ceiling completion across 81 domains with 4 new engine domains: Global Illumination and Decals in gi_manage, input simulation and macro replay in input_event_manage, direct 2D/3D physics space state raycasts in physics_query_manage, and curves, bezier splines, and gradients in curve_manage.

### Added

- **OpenAI Custom GPT 30-Action Adaptation**:
  - `godot_ai.transport.openapi`: Added compact schema mode (under 25 operations) respecting OpenAI's strict 30-operation cap on Custom GPT Actions. Exposes universal router `/api/v1/call` allowing cloud GPTs to invoke any of the 100 tools dynamically.
  - `godot_ai.transport.rest_gateway`: `/openapi.json` now defaults to compact schema for instant ChatGPT Custom GPT Action import; added `/openapi-full.json` and `?mode=full` for unrestricted clients.
- **Zero-Install Cloud Tunneling via SSH**:
  - `godot_ai.transport.tunnel`: Added automated SSH reverse tunneling (`--tunnel ssh`, `pinggy`, `localhost.run`) using built-in system OpenSSH (`ssh`), enabling public HTTPS tunnels on Windows, macOS, and Linux without installing third-party binaries.
- **Cloud Container Headless Sandbox**:
  - `godot_ai.cloud_sandbox`: Standalone headless Godot runner for ChatGPT Code Interpreter / cloud containers; automatically provisions official Godot 4 headless Linux binaries, runs GDScript scripts, and validates scenes in cloud sandboxes without display servers.
  - `godot_ai.remote`: Added `check_connection` and `batch` helper methods to `RemoteGodotClient`.
- **Global Illumination & Decal Management (`gi_manage`)**:
  - Introduced `gi_manage` tool and `GIHandler` for lighting and projection.
  - `create_decal`: Create Decal nodes with dimensions and PBR textures.
  - `configure_decal`: Tune decal emission, fade, and texture maps.
  - `create_reflection_probe`: Create ReflectionProbe nodes for local specular reflections.
  - `create_voxel_gi`: Create VoxelGI nodes for real-time indirect bounce lighting.
  - `create_lightmap_gi`: Create LightmapGI nodes for baked lighting.
  - `get_gi_info`: Inspect active lighting probe and decal settings.
- **Input Simulation & Macro Replay (`input_event_manage`)**:
  - Introduced `input_event_manage` tool and `InputEventHandler` for gameplay testing.
  - `simulate_action`: Simulate virtual action presses and releases with custom strength.
  - `simulate_key`: Simulate keyboard key taps and hold events.
  - `simulate_mouse_button`: Simulate mouse button clicks at specified coordinates.
  - `simulate_mouse_motion`: Simulate mouse motion and velocity.
  - `replay_macro`: Replay sequential input events for automated game testing.
  - `get_input_state`: Query action pressed states and strengths.
- **Physics Space State Direct Queries (`physics_query_manage`)**:
  - Introduced `physics_query_manage` tool and `PhysicsQueryHandler` for space state queries without scene tree node allocation.
  - `intersect_ray_3d` / `intersect_ray_2d`: Perform direct 3D and 2D physics raycasts.
  - `intersect_point_3d` / `intersect_point_2d`: Query colliders overlapping a point in world space.
  - `intersect_shape_3d`: Query colliders overlapping shapes in 3D.
  - `cast_motion_3d`: Predict collision fractions for moving shapes.
- **Curves, Splines, and Gradients (`curve_manage`)**:
  - Introduced `curve_manage` tool and `CurveHandler` for mathematical curves and ramps.
  - `create_curve_1d`: Generate 1D interpolation and easing Curve resources.
  - `create_curve_2d`: Generate 2D bezier spline Curve2D resources.
  - `create_curve_3d`: Generate 3D bezier spline Curve3D resources.
  - `create_gradient`: Generate multi-stop color ramp Gradient resources.
  - `create_gradient_texture`: Generate GradientTexture1D and GradientTexture2D resources.
  - `sample_curve`: Sample curve values or baked positions.
  - `sample_gradient`: Sample RGBA colors on gradients.

## 5.0.25 (2026-09-22)

ChatGPT Web & Cloud Computer Mode integration, OpenAPI 3.1 REST gateway, public tunnel automation, and complete engine expansion with 6 new domains: physics bodies in body_manage, world environment and fog in world_manage, audio DSP effects in audio_effect_manage, navigation pathfinding queries in nav_query_manage, standalone CLI execution in headless_manage, and cloud bridge status in cloud_manage.

### Added

- **ChatGPT Web & Cloud Computer Mode Integration**:
  - `godot_ai.transport.openapi`: Automated OpenAPI 3.1.0 schema generator exposing all registered MCP tools as REST endpoints for ChatGPT Custom GPT Actions.
  - `godot_ai.transport.rest_gateway`: High-performance Starlette REST gateway routes (`/openapi.json`, `/api/v1/tools/{name}`, `/api/v1/call`, `/api/v1/tools`, `/api/v1/status`) supporting optional Bearer token authentication.
  - `godot_ai.transport.tunnel`: Zero-config Cloudflare Quick Tunnel and ngrok supervisor for exposing local Godot instances to web and cloud assistants with instant public HTTPS URLs.
  - `godot_ai.remote`: Lightweight `RemoteGodotClient` Python SDK runnable in ChatGPT Advanced Data Analysis / cloud sandboxes or external machines without local engine installation.
  - CLI enhancements: Added `--tunnel` and `--auth-token` options, plus `godot-ai tunnel` subcommand.
- **Physics Body & Collision Management (`body_manage`)**:
  - Introduced `body_manage` tool and `BodyHandler` for RigidBody, CharacterBody, and StaticBody configurations.
  - `configure_body`: Set mass, gravity_scale, linear_damp, angular_damp, and freeze properties.
  - `apply_impulse`: Apply 2D and 3D central impulses and offset forces to RigidBody nodes.
  - `set_collision_layer_mask`: Configure collision_layer, collision_mask, and collision_priority.
  - `scaffold_character_body`: Scaffold CharacterBody2D and CharacterBody3D with collision shapes.
  - `get_body_info`: Inspect physics properties, velocity, and collision masks.
- **WorldEnvironment, Sky, and Fog Pipeline (`world_manage`)**:
  - Introduced `world_manage` tool and `WorldHandler` for post-processing and volumetric effects.
  - `configure_world_environment`: Configure ambient light, tonemap, ssao, ssr, sdfgi, and glow.
  - `create_sky_material`: Setup procedural or panorama sky materials on Environment resources.
  - `set_volumetric_fog`: Enable and tune volumetric fog density, albedo, emission, and length.
  - `configure_camera_attributes`: Configure CameraAttributesPractical and Physical settings.
  - `get_world_info`: Inspect active environment, sky, and post-processing properties.
- **AudioServer DSP Bus Effects (`audio_effect_manage`)**:
  - Introduced `audio_effect_manage` tool and `AudioEffectHandler` for audio bus signal processing.
  - `add_effect_to_bus`: Add AudioEffect instances (Reverb, Delay, Distortion, Chorus, EQ, Compressor, PitchShift) to audio buses.
  - `configure_effect`: Configure DSP parameters and enabled state on bus effects.
  - `remove_effect`: Remove audio effects from buses by index.
  - `list_bus_effects`: List all effects, classes, and active states on an audio bus.
- **Navigation Queries and Spatial Pathfinding (`nav_query_manage`)**:
  - Introduced `nav_query_manage` tool and `NavQueryHandler` for direct NavigationServer queries.
  - `query_path_2d`: Query 2D navigation paths across navmeshes between points.
  - `query_path_3d`: Query 3D navigation paths across navmeshes between points.
  - `scaffold_nav_link`: Scaffold NavigationLink2D and NavigationLink3D connecting disjoint regions.
  - `scaffold_nav_obstacle`: Scaffold NavigationObstacle2D and NavigationObstacle3D for dynamic avoidance.
  - `get_nav_map_info`: Inspect navigation map cell sizes, margins, and region counts.
- **Headless CLI & Standalone Engine Execution (`headless_manage`)**:
  - Introduced `headless_manage` tool and `HeadlessHandler` for CLI and non-GUI operations.
  - `run_script`: Execute GDScript files or inline code snippets in headless engine mode.
  - `run_headless_scene`: Execute scenes headlessly with frame limits for simulations or CI tests.
  - `export_project_cli`: Trigger headless project exports via Godot export presets.
  - `reimport_assets_cli`: Reimport project assets via headless editor pass.
  - `get_engine_info`: Inspect Godot version, architecture, and CLI capabilities.
- **Cloud Bridge and Tunnel Metadata (`cloud_manage`)**:
  - Introduced `cloud_manage` tool and `CloudHandler` for tunnel and cloud status introspection.
  - `get_tunnel_status`: Inspect active tunnel state, port, and endpoint URLs.
  - `get_action_schema_url`: Retrieve OpenAPI schema URL and setup instructions for ChatGPT Custom GPT.
  - `test_cloud_connection`: Test round-trip latency and operational connectivity between editor and gateway.

## 5.0.24 (2026-09-22)

Complete Godot 4 engine coverage closing all remaining subsystem gaps: texture and image processing in texture_manage, font resources and variations in font_manage, low-level TCP/UDP and WebSocket scaffolding in network_manage, visual shader node graphs in visual_shader_manage, animation state machines and blend trees in animation_tree_manage, animated sprites, MultiMesh, and Line2D in sprite_manage, persistent editor settings in editor_settings_manage, 2D and 3D physics joints in joint_manage, 2D and 3D occlusion culling in occluder_manage, ConfigFile INI and JSON utilities in config_manage, and parallax background and canvas layers in parallax_manage.

### Added

- **Texture and Image Resource Pipeline (`texture_manage`)**:
  - Introduced `texture_manage` tool and `TextureManageHandler` for Image, AtlasTexture, and CurveTexture creation.
  - `create_image`: Create new Image resources with customizable width, height, mipmaps, format (RGBA8, RGB8, R8), fill color, and save to disk.
  - `create_atlas`: Create AtlasTexture resources referencing sub-regions of existing textures with filter clipping.
  - `get_texture_info`: Inspect dimensions, format, and class of texture and image resources.
  - `create_curve_texture`: Generate procedural CurveTexture resources from control points.
- **Font Resources and Typography (`font_manage`)**:
  - Introduced `font_manage` tool and `FontHandler` for typography, SystemFont, and LabelSettings.
  - `create_system_font`: Instantiate SystemFont resources querying operating system font fallback lists.
  - `create_font_variation`: Create FontVariation resources with custom boldness, OpenType tags, and spacing.
  - `create_label_settings`: Create reusable LabelSettings with font styling, outline, and shadow configurations.
  - `get_font_info`: Inspect properties and type of font resources.
- **Low-Level Networking and Sockets (`network_manage`)**:
  - Introduced `network_manage` tool and `NetworkHandler` for TCP, UDP, and WebSocket networking.
  - `scaffold_tcp_server`: Scaffold TCP server listener nodes with port and bind address configurations.
  - `scaffold_websocket_peer`: Scaffold WebSocket client and peer nodes for real-time networking.
  - `scaffold_udp_peer`: Scaffold UDP packet peer nodes for low-latency datagram networking.
  - `get_network_interfaces`: Inspect local host IP addresses and network adapter interfaces via IP.
- **VisualShader Graph Construction (`visual_shader_manage`)**:
  - Introduced `visual_shader_manage` tool and `VisualShaderHandler` for visual shader node graphs.
  - `create_visual_shader`: Create VisualShader resources for spatial, canvas_item, particles, sky, and fog.
  - `add_node`: Add VisualShaderNode elements into shader stages with position coordinates.
  - `connect_nodes`: Connect node output ports to input ports in visual shader graphs.
  - `get_graph`: Enumerate all nodes, positions, and connections in a VisualShader graph.
- **AnimationTree State Machines and Blend Trees (`animation_tree_manage`)**:
  - Introduced `animation_tree_manage` tool and `AnimationTreeHandler` for state machines and blend trees.
  - `scaffold_state_machine`: Scaffold AnimationTree nodes with AnimationNodeStateMachine root.
  - `add_state`: Add animation states into state machines referencing AnimationPlayer animations.
  - `add_transition`: Create transitions between animation states with auto-advance and switch modes.
  - `scaffold_blend_tree`: Scaffold AnimationTree nodes with AnimationNodeBlendTree root.
  - `get_tree_info`: Inspect tree root class, active state, and connected animation players.
- **Sprites, MultiMesh, and Vector Lines (`sprite_manage`)**:
  - Introduced `sprite_manage` tool and `SpriteHandler` for 2D/3D sprite animation and instancing.
  - `create_sprite_frames`: Create SpriteFrames resources with multiple named animations and frame rates.
  - `scaffold_animated_sprite`: Scaffold AnimatedSprite2D and AnimatedSprite3D nodes.
  - `scaffold_multimesh`: Scaffold high-performance MultiMeshInstance2D and MultiMeshInstance3D nodes.
  - `configure_line_2d`: Configure points, width, and colors for Line2D vector rendering.
- **Persistent Editor Settings (`editor_settings_manage`)**:
  - Introduced `editor_settings_manage` tool and `EditorSettingsHandler` for editor preferences and paths.
  - `get_setting`: Read editor configuration values by path via EditorInterface.get_editor_settings().
  - `set_setting`: Write editor preferences and configurations persistently.
  - `list_settings`: Search and enumerate editor setting key paths by prefix.
  - `get_editor_paths`: Retrieve configuration, data, and cache directory locations via EditorPaths.
- **2D and 3D Physics Joints (`joint_manage`)**:
  - Introduced `joint_manage` tool and `JointHandler` for physics body constraints.
  - `scaffold_joint_2d`: Create PinJoint2D, GrooveJoint2D, and DampedSpringJoint2D constraints.
  - `scaffold_joint_3d`: Create PinJoint3D, HingeJoint3D, SliderJoint3D, ConeTwistJoint3D, and Generic6DOFJoint3D.
  - `configure_joint`: Update joint parameters, softness, bias, and angular/linear limits.
  - `get_joint_info`: Inspect joint type, connected node paths, and active properties.
- **2D and 3D Occlusion Culling (`occluder_manage`)**:
  - Introduced `occluder_manage` tool and `OccluderHandler` for visibility culling optimization.
  - `scaffold_occluder_3d`: Create OccluderInstance3D nodes with BoxOccluder3D, SphereOccluder3D, or QuadOccluder3D.
  - `scaffold_occluder_2d`: Create LightOccluder2D nodes with OccluderPolygon2D shapes.
  - `get_occluder_info`: Inspect occluder nodes and attached shape resources.
- **ConfigFile, JSON, and Expression Utilities (`config_manage`)**:
  - Introduced `config_manage` tool and `ConfigHandler` for game configuration and data serialization.
  - `config_read`: Read INI-formatted ConfigFile resources by section and key or entire dictionaries.
  - `config_write`: Write section and key values into INI-formatted ConfigFile resources.
  - `json_parse`: Parse JSON strings safely into Godot Variant data structures.
  - `json_generate`: Serialize Godot Variant data into formatted JSON strings.
  - `expression_eval`: Compile and execute math and logic expressions dynamically via Godot Expression.
- **Parallax Backgrounds and Canvas Layers (`parallax_manage`)**:
  - Introduced `parallax_manage` tool and `ParallaxHandler` for layered 2D rendering and visibility.
  - `scaffold_parallax`: Create Parallax2D or ParallaxBackground nodes with scroll scale and repeat size.
  - `scaffold_canvas_layer`: Create CanvasLayer nodes with custom layer depth and follow viewport mode.
  - `scaffold_visibility_notifier`: Create VisibleOnScreenNotifier2D and VisibleOnScreenNotifier3D nodes.
  - `get_parallax_info`: Inspect parallax and canvas layer node properties.

## 5.0.23 (2026-09-22)

PCK virtual packaging and DLC loading, OS/hardware introspection and time controls, 2D/3D lighting and decals, in-engine HTTP networking and downloads, global shader parameters, and viewport capture and MovieWriter automation: PCKPacker and ProjectSettings.load_resource_pack in pck_manage, OS/Time/DisplayServer and Engine.time_scale in system_manage, Directional/Omni/Spot lights, Decals, and Reflection/GI probes in light_manage, HTTPRequest scaffolding, REST requests, and file downloads in http_manage, project-wide uniform variables via RenderingServer.global_shader_parameter in shader_global_manage, and viewport image export and MovieWriter video capture in recording_manage.

### Added

- **PCK and Mod Virtual Packaging (`pck_manage`)**:
  - Introduced `pck_manage` tool and `PckHandler` for DLC and virtual resource pack automation.
  - `create_pck`: Pack project resource files into standalone .pck files via PCKPacker with customizable alignment.
  - `load_pck`: Dynamically mount .pck files into the virtual filesystem via ProjectSettings.load_resource_pack with replace flag.
  - `inspect_pck`: Check file existence and size in bytes for a target .pck package.
- **System, OS, Time, and Engine Controls (`system_manage`)**:
  - Introduced `system_manage` tool and `SystemHandler` for engine environment and hardware introspection.
  - `get_system_info`: Inspect OS name, version, processor count, device model, video adapter name/vendor, and locale.
  - `get_time`: Query high-precision Unix epoch timestamp, ISO 8601 string, timezone offset, and datetime dictionary.
  - `set_time_scale`: Speed up or slow down the game engine via Engine.time_scale (e.g. for hyper-speed simulation or slow-motion replay).
  - `get_clipboard` / `set_clipboard`: Read and set operating system clipboard content via DisplayServer.
  - `get_env` / `set_env`: Read and set environment variables for the running engine process via OS.
- **2D and 3D Lighting, Shadows, Decals, and Probes (`light_manage`)**:
  - Introduced `light_manage` tool and `LightHandler` for complete illumination and probe setups.
  - `scaffold_light_3d`: Instantiate and configure DirectionalLight3D, OmniLight3D, or SpotLight3D with color, energy, range, attenuation, spot angle, and shadows.
  - `scaffold_light_2d`: Instantiate PointLight2D or DirectionalLight2D with color, energy, and shadows.
  - `scaffold_decal`: Create Decal projection nodes with size volume and albedo texture.
  - `scaffold_probe`: Instantiate ReflectionProbe, LightmapGI, or VoxelGI nodes.
  - `set_light_properties`: Dynamically modify energy, color, shadows, and volumetric fog energy on existing light nodes.
  - `get_light_info`: Inspect active lighting properties of any 2D or 3D light node.
- **In-Engine HTTP Networking and Downloads (`http_manage`)**:
  - Introduced `http_manage` tool and `HttpHandler` for REST and web communication.
  - `scaffold_http_request`: Instantiate HTTPRequest nodes into scene trees with configurable timeouts.
  - `send_request`: Execute in-engine HTTP REST requests (GET, POST, PUT, DELETE, HEAD, OPTIONS) through Godot's network stack.
  - `download_file`: Download remote files directly into the project filesystem (res:// or user://).
- **Global Shader Parameters (`shader_global_manage`)**:
  - Introduced `shader_global_manage` tool and `ShaderGlobalHandler` for project-wide shader uniforms.
  - `list_globals`: Enumerate all global shader parameters defined in RenderingServer.
  - `set_global`: Update runtime values of global shader parameters (float, int, bool, Color, Vector2/3/4).
  - `add_global`: Define new global shader parameters and persist to ProjectSettings (shader_globals/).
  - `remove_global`: Remove global shader parameters from RenderingServer and ProjectSettings.
- **Viewport Frame Capture and MovieWriter Recording (`recording_manage`)**:
  - Introduced `recording_manage` tool and `RecordingHandler` for automated rendering capture and video recording.
  - `capture_viewport`: Extract viewport texture and save directly to PNG image files on disk.
  - `configure_movie_writer`: Configure editor MovieWriter settings in ProjectSettings (movie_file, fps, mjpeg_quality).
  - `get_writer_status`: Check if MovieWriter mode is active and inspect configured output video path.

## 5.0.22 (2026-09-21)

Paths and curves spline automation, procedural 3D mesh synthesis and deformation, WorldEnvironment lighting and post-processing, skeletal rigging and ragdoll scaffolding, cryptography and secure hashing, and editor plugin lifecycle management: Curve2D/Curve3D and spline generation in path_manage, SurfaceTool and MeshDataTool procedural meshes in mesh_manage, post-processing and visual presets in rendering_manage, bone poses and ragdolls in skeleton_manage, secure hashing and TLS certificates in crypto_manage, and addon discovery and EditorPlugin scaffolding in plugin_manage.

### Added

- **Paths and Curve Spline Automation (`path_manage`)**:
  - Introduced `path_manage` tool and `PathHandler` for programmatic curve and spline workflows.
  - `create_curve_2d` / `create_curve_3d`: Construct Curve2D or Curve3D resources with Bezier control points and optional file persistence.
  - `scaffold_path`: Instantiate Path2D or Path3D nodes with optional PathFollow child, configuring progress, loop, and rotation flags.
  - `sample_baked_points`: Sample baked positions, lengths, and intervals along paths for precision AI navigation, camera rails, or projectile paths.
  - `generate_spline`: Procedurally generate common spline shapes (circle loop, S-curve, sine wave, rectangular patrol route, spiral).
- **Procedural 3D Mesh Synthesis and Manipulation (`mesh_manage`)**:
  - Introduced `mesh_manage` tool and `MeshHandler` interfacing with SurfaceTool, MeshDataTool, and PrimitiveMesh.
  - `generate_surface_mesh`: Construct custom ArrayMesh geometry via SurfaceTool with vertices, normals, UVs, vertex colors, indices, and automatic normal/tangent calculation.
  - `deform_mesh`: Inspect and transform existing mesh vertices via MeshDataTool, applying height displacement, tapering, or axis scaling, and re-committing to ArrayMesh.
  - `create_primitive`: Generate parameterized PrimitiveMesh resources (BoxMesh, SphereMesh, CylinderMesh, CapsuleMesh, TorusMesh, PlaneMesh, PrismMesh) with custom subdivisions and materials.
  - `get_mesh_info`: Inspect mesh surface count, vertex count, face count, and AABB bounds.
- **World Environment and Lighting Post-Processing (`rendering_manage`)**:
  - Introduced `rendering_manage` tool and `RenderingHandler` managing environments and post-processing.
  - `scaffold_world_environment`: Create WorldEnvironment nodes with procedural/physical skies, ambient lighting, and tonemapping modes.
  - `set_environment_effects`: Configure Glow/Bloom, SSR, SSAO, SSIL, SDFGI, and Volumetric Fog.
  - `set_camera_attributes`: Configure CameraAttributesPractical / CameraAttributesPhysical (Auto Exposure, Depth of Field near/far blur).
  - `apply_lighting_preset`: Apply curated visual presets ("outdoor_sunny", "dungeon_dark", "scifi_cyberpunk", "retro_pixel", "cinematic_moody").
  - `get_environment_info`: Query current active environment properties, background mode, and active post-processing toggles.
- **Skeletal Rigging, Sockets, and Ragdolls (`skeleton_manage`)**:
  - Introduced `skeleton_manage` tool and `SkeletonHandler` connecting to Skeleton3D systems.
  - `get_skeleton_info`: Inspect bone hierarchy, bone names, parent indices, rest transforms, and current pose transforms.
  - `set_bone_pose`: Modify position, rotation (quaternion or euler), or scale for specific bones.
  - `scaffold_bone_attachment`: Instantiate BoneAttachment3D nodes linked to designated bones for equipment and weapon sockets.
  - `scaffold_ragdoll`: Automatically generate PhysicalBone3D hierarchies and collision shapes for a Skeleton3D.
- **Cryptography and Secure Hashing (`crypto_manage`)**:
  - Introduced `crypto_manage` tool and `CryptoHandler` integrating Godot's Crypto singleton and HashingContext.
  - `hash_file` / `hash_string`: Compute SHA-256, SHA-1, or MD5 checksums of files or string payloads.
  - `generate_random_bytes`: Generate cryptographically secure random bytes or hex tokens.
  - `generate_rsa_key`: Generate RSA key pairs for asymmetric encryption and signing.
  - `generate_self_signed_cert`: Generate self-signed X509 certificates for local HTTPS, WSS, or multiplayer authentication.
  - `hmac_digest`: Compute HMAC authentication digests.
- **Editor Plugin and Addon Lifecycle (`plugin_manage`)**:
  - Introduced `plugin_manage` tool and `PluginHandler` managing project addons.
  - `list_plugins`: Scan res://addons/ for all plugin.cfg descriptors and report name, description, author, version, script, and enabled state.
  - `set_plugin_enabled`: Enable or disable an addon in editor_plugins/enabled within ProjectSettings.
  - `scaffold_plugin`: Generate complete boilerplate for a new custom EditorPlugin (manifest plugin.cfg, main plugin script with _enter_tree / _exit_tree, and dock UI scaffolding).

## 5.0.21 (2026-09-21)

DisplayServer and Window management, background threaded resource loading, GPU compute shaders, project export automation, OpenXR AR/VR rigging, and editor undo/redo transactions: DisplayServer geometry and sub-window scaffolding in display_manage, background resource streaming and loading screens in loader_manage, RenderingDevice compute shader dispatch in compute_manage, export preset inspection and automated builds in export_manage, OpenXR rigging and tracking in xr_manage, and EditorUndoRedoManager history introspection in undo_redo_manage.

### Added

- **DisplayServer and Window Management (`display_manage`)**:
  - Introduced `display_manage` tool and `DisplayHandler` for direct control over DisplayServer and Window nodes.
  - `get_window_info`: Query current window mode, position, size, screen count, DPI, refresh rate, and VSync mode.
  - `set_window_mode`: Configure window mode (windowed, minimized, maximized, fullscreen, exclusive fullscreen).
  - `set_window_properties`: Modify borderless flags, always-on-top status, transparent background, and min/max window dimensions.
  - `set_mouse_mode`: Set mouse capture mode (visible, hidden, captured, confined).
  - `scaffold_dialog`: Create and configure popups, ConfirmationDialog, FileDialog, or custom SubWindows.
- **Background Threaded Resource Loading (`loader_manage`)**:
  - Introduced `loader_manage` tool and `LoaderHandler` interfacing with ResourceLoader threaded loading.
  - `load_threaded`: Initiate asynchronous threaded loading for large scenes, textures, and assets via ResourceLoader.load_threaded_request.
  - `get_status`: Poll threaded load progress and status (invalid, in progress, failed, ready).
  - `get_resource`: Finalize and retrieve loaded resources once threaded requests complete.
  - `scaffold_loading_screen`: Generate responsive loading screen scenes and scripts with progress bars and smooth scene transitions.
- **GPU Compute Shaders and RenderingDevice (`compute_manage`)**:
  - Introduced `compute_manage` tool and `ComputeHandler` enabling GPU compute pipelines.
  - `create_shader`: Scaffold GLSL compute shader files with standard uniform buffer and invocation templates.
  - `dispatch`: Execute compute shaders via RenderingDevice with storage buffers, uniforms, and workgroup dispatch configurations.
  - `get_device_info`: Query active RenderingDevice capabilities, device names, and driver version.
- **Project Export Automation (`export_manage`)**:
  - Introduced `export_manage` tool and `ExportHandler` automating project build pipelines.
  - `list_presets`: Parse export_presets.cfg and report all defined platform presets and target paths.
  - `get_preset_info`: Inspect detailed export preset configurations and feature flags.
  - `export_project`: Execute headless godot --export-release or --export-debug builds for target presets.
- **OpenXR AR/VR Rigging and Status (`xr_manage`)**:
  - Introduced `xr_manage` tool and `XrHandler` integrating OpenXR and spatial computing workflows.
  - `scaffold_xr_player`: Scaffold complete XROrigin3D hierarchies with XRCamera3D, left/right XRController3D nodes, hand trackers, and basic teleport movement.
  - `get_xr_status`: Query OpenXR runtime initialization, tracking status, and head/controller poses.
  - `generate_bootstrap_script`: Generate production OpenXR interface initialization and pass-through management scripts.
- **Editor Undo/Redo Introspection (`undo_redo_manage`)**:
  - Introduced `undo_redo_manage` tool and `UndoRedoHandler` connecting to EditorUndoRedoManager.
  - `get_history`: Query undo/redo transaction stack, current action index, and action names.
  - `undo`: Undo the most recent editor action.
  - `redo`: Redo the previously reverted action.

## 5.0.20 (2026-09-21)

Viewport and splitscreen management, high-level multiplayer scaffolding, procedural tweens and motion recipes, and engine diagnostics: SubViewport creation and multi-player splitscreen scaffolding in viewport_manage, ENetMultiplayerPeer and replication configuration in multiplayer_manage, procedural game-feel juice animations and code generation in tween_manage, and real-time Performance monitors and memory breakdowns in profiler_manage.

### Added

- **Viewport and Multi-Player Splitscreen Management (`viewport_manage`)**:
  - Introduced `viewport_manage` tool and `ViewportHandler` providing direct control over Godot Viewports and render targets.
  - `create_subviewport`: Create standalone SubViewports or wrapped SubViewportContainers with configurable size, update modes, transparency, and 3D world isolation.
  - `scaffold_splitscreen`: Scaffold complete 2-player horizontal, 2-player vertical, or 4-player quad splitscreen layouts with independent cameras and audio listeners.
  - `wire_render_texture`: Route a SubViewport's ViewportTexture directly into Sprite2D, TextureRect, or MeshInstance3D albedo materials.
  - `get_viewport_tree`: Inspect all Viewports in the active scene, their dimensions, update modes, and active 2D/3D cameras.
  - `set_properties`: Configure Viewport MSAA, screen-space antialiasing, HDR 2D, and render update properties.
- **High-Level Multiplayer Networking Scaffolding (`multiplayer_manage`)**:
  - Introduced `multiplayer_manage` tool and `MultiplayerHandler` integrating Godot's high-level multiplayer networking architecture.
  - `scaffold_network_manager`: Generate production-grade ENetMultiplayerPeer network manager scripts with host/join/disconnect routines and peer lifecycle signals.
  - `scaffold_spawner`: Instantiate and configure MultiplayerSpawner nodes with auto-spawn flags and registered spawnable scenes.
  - `scaffold_synchronizer`: Instantiate and configure MultiplayerSynchronizer nodes with declarative SceneReplicationConfig properties.
  - `get_network_status`: Query active MultiplayerAPI state, server role, unique peer ID, and connected peers.
- **Procedural Tweens and Motion Recipes (`tween_manage`)**:
  - Introduced `tween_manage` tool and `TweenHandler` providing procedural motion, game-feel juice animations, and code generation.
  - `create`: Construct and run property interpolations with configurable transition curves, ease modes, delays, and relative offsets.
  - `preset_animation`: Execute game-feel recipes including punch_scale, shake_2d, float_bob, fade, flash_color, progress_fill, bounce_in, and spin.
  - `generate_code`: Generate production GDScript Tween snippets for copy-paste or programmatic attachment.
- **Performance Profiler and Engine Diagnostics (`profiler_manage`)**:
  - Introduced `profiler_manage` tool and `ProfilerHandler` querying real-time engine performance metrics.
  - `get_monitors`: Read key Performance monitors (FPS, process time, physics process time, draw calls, object counts, memory, and audio latency).
  - `get_memory_info`: Retrieve structured memory statistics including static memory, peak memory, texture memory, buffer memory, and node counts.
  - `get_render_info`: Inspect active draw calls, primitive counts, 2D/3D render objects, and VRAM utilization.
  - `get_physics_info`: Query 2D and 3D physics server statistics including active bodies, collision pairs, and physics islands.

## 5.0.19 (2026-09-21)

Engine geometry synthesis, localization pipeline, audio bus routing, and advanced physics queries: Comprehensive 2D and 3D procedural geometry via geometry_manage, full TranslationServer and CSV localization via localization_manage, in-depth AudioServer bus and DSP effect management in audio_manage, 3D point queries and ShapeCast sensors in physics_manage, and comprehensive project metadata querying in project_manage.

### Added

- **Procedural Geometry and Mesh Synthesis (`geometry_manage`)**:
  - Introduced `geometry_manage` tool and `GeometryHandler` providing direct access to Godot's Geometry2D and SurfaceTool pipelines.
  - `polygon_boolean`: Perform 2D constructive solid polygon operations (merge, difference, intersection, xor) via Geometry2D.
  - `polygon_offset`: Inflate or deflate 2D polygons with configurable delta and join types (square, round, miter).
  - `triangulate`: Decompose 2D polygons into index arrays for mesh and collision generation via Geometry2D.triangulate_polygon.
  - `convex_hull`: Compute 2D convex hull wrapping arbitrary point sets via Geometry2D.convex_hull.
  - `scaffold_polygon_2d`: Instantiate and attach Polygon2D or CollisionPolygon2D nodes directly into active scenes.
  - `generate_mesh`: Generate procedural 3D meshes (cube, plane, pyramid) via SurfaceTool, supporting direct scene attachment or resource saving to res://.
- **Localization and Translation System (`localization_manage`)**:
  - Introduced `localization_manage` tool and `LocalizationHandler` integrating TranslationServer and CSV-based translation workflows.
  - `scaffold_csv`: Generate standard multi-language CSV files and automatically register them in ProjectSettings.
  - `add_entry`: Insert or update translation rows with multi-language strings in project localization CSV files.
  - `get_locales`: Query loaded locales, fallback locales, and translation domains from TranslationServer.
  - `set_locale`: Set the active test locale in TranslationServer for immediate in-editor preview.
  - `translate`: Translate message keys via TranslationServer with context support.
  - `extract_strings`: Scan project GDScript and scene files for tr() message lookup occurrences.
- **AudioServer Bus and DSP Effect Management (`audio_manage`)**:
  - Expanded `audio_manage` with comprehensive AudioServer bus routing and effect management.
  - `bus_list`: Query all active audio buses, volume decibels, routing targets, and DSP effects.
  - `bus_add`: Create new audio buses routed to designated parent buses.
  - `bus_remove`: Remove audio buses by name or index.
  - `bus_set_properties`: Atomically configure bus volume, mute, solo, and effect bypass flags.
  - `bus_add_effect`: Attach audio effects (Reverb, Delay, Chorus, Phaser, Distortion, EQ, Compressor, Limiter, LowPassFilter, HighPassFilter, BandPassFilter, NotchFilter, Amplify) with parameter tuning.
  - `bus_save_layout`: Persist current AudioServer bus layouts to .tres resource files.
- **Advanced Physics Queries and Layer Management (`physics_manage`)**:
  - `query_point_3d`: Query physics bodies and areas intersecting a given 3D world coordinate via PhysicsServer3D.
  - `shapecast_scaffold`: Instantiate and attach ShapeCast2D or ShapeCast3D sweep sensors with configurable collision shapes.
  - `set_layer_names`: Configure human-readable names for 2D/3D physics and render layers in ProjectSettings.
  - `get_layer_names`: Read configured layer names across physics, render, and navigation layers.
- **Project Metadata Snapshot (`project_manage`)**:
  - Added `get_info` operation returning Godot engine version, project name, path, display settings, rendering method, and registered autoloads.

## 5.0.18 (2026-09-21)

Universal Godot engine access, reflection, and total automation expansion: Universal engine control and arbitrary GDScript evaluation in the editor process via omni_manage, complete visual shader synthesis with production game presets via shader_manage, direct space-state physics queries and sensor scaffolding via physics_manage, editor-process GDScript evaluation in editor_manage, and universal node method invocation in node_manage.

### Added

- **Universal Godot Control and Reflection Domain (`omni_manage`)**:
  - Full server wiring and dispatch for `omni_manage` supporting universal engine control across the entire C++ ClassDB, engine singletons, editor UI, and runtime.
  - Operations include `eval` (arbitrary GDScript execution with full EditorInterface permissions), `call` (invoke any method on any Node, Resource, Singleton, or RefCounted object with arbitrary arguments), `get` (read any property), `set` (write any property), `inspect` (full inspection of methods, properties, and signals), `instantiate` (instantiate any engine class or script), `ui_tree` (hierarchical semantic editor UI control tree), `ui_click` (simulate click on editor controls), `ui_type` (type text into editor text inputs), `instantiate_prefab` (instantiate scene prefabs), `shader_create`, `mesh_primitive`, `collision_shape`, `preset_motion`, and `ping`.
  - Enhanced object resolution supporting scene-root relative node paths, EditorInterface, engine singletons, res:// resources, and object instance IDs.
- **Shader System and Visual Effect Management (`shader_manage`)**:
  - Introduced `shader_manage` tool and `ShaderHandler` supporting programmatic shader creation, compilation, uniform parameter tuning, and production shader presets.
  - Shader presets include `outline_2d` (sprite border outline with width and color), `hit_flash` (damage flash with color and modifier), `dissolve_2d` (noise-based burning dissolve with glowing edge border), `water_2d` (wave distortion and reflection), `foliage_wind` (vertex-displacement wind sway), `crt_scanline` (retro CRT curvature, scanlines, and vignette), and `hologram_glitch` (holographic scanline glitch).
  - Operations include `create`, `apply_preset`, `set_param`, and `get_params`.
- **Physics Queries and Sensor Scaffolding (`physics_manage`)**:
  - Introduced `physics_manage` tool and `PhysicsHandler` providing direct space-state raycasting, collision queries, and sensor generation.
  - `raycast_2d`: Performs 2D direct raycasts via PhysicsServer2D space state returning hit status, collision position, surface normal, collider node path, and shape.
  - `raycast_3d`: Performs 3D direct raycasts via PhysicsServer3D space state returning hit status, collision position, surface normal, collider node path, and shape.
  - `query_point_2d`: Queries physics bodies and areas intersecting a given 2D world coordinate.
  - `scaffold_sensor`: Instantiates and attaches RayCast2D or RayCast3D sensor nodes with target positions, collision masks, and auto-wiring.
- **Editor-Process Script Evaluation (`editor_manage`)**:
  - Added `eval` and `execute_script` operations to `editor_manage` allowing execution of GDScript code expressions and script files directly in the editor process context.
- **Universal Node Method Invocation (`node_manage`)**:
  - Added `call_method` operation to `node_manage` allowing invocation of any method on any node in the active scene tree with arbitrary arguments.

## 5.0.17 (2026-09-21)

Autonomous game systems and persistence expansion: Dialogue and branching narrative system scaffolding with typewriter effects, corruption-resistant atomic save and load persistence with group-based state serialization, modular node-based finite state machines with character and enemy AI presets, single-call UI theme presets across classic and modern aesthetics, multi-channel sound effect manager with audio player pooling, and test instructions parity hardening.

### Added

- **Dialogue and Narrative System Management**: Introduced `dialogue_manage` tool and `DialogueHandler` with `scaffold_system` and `create_dialogue` operations.
  - `scaffold_system`: Scaffolds a complete `DialogueManager` singleton and `DialogueBox` CanvasLayer UI scene featuring typewriter text animation, BBCode styling, speaker labels, continue prompt, and dynamic branching choice buttons, wired to typed signals (`dialogue_started`, `line_displayed`, `choices_presented`, `choice_selected`, `dialogue_ended`).
  - `create_dialogue`: Creates structured branching dialogue graphs in JSON/Resource format with speaker designations, localized dialogue strings, and choice jump targets.
- **Save and Load Persistence Management**: Introduced `save_manage` tool and `SaveHandler` with atomic file persistence operations (`scaffold_save_system`, `save_slot`, `load_slot`, `list_slots`, `delete_slot`).
  - `scaffold_save_system`: Scaffolds an atomic, corruption-resistant `SaveManager` singleton using temporary-file writes and renames. Automatically gathers state from all nodes in the 'saveable' group implementing `save_state()`, restores state via `load_state()`, manages save slot directories, and provides optional password encryption.
  - `save_slot`, `load_slot`, `list_slots`, `delete_slot`: In-editor inspection and testing of save slot files and metadata in `user://saves/`.
- **Finite State Machine Architecture**: Introduced `fsm_manage` tool and `FsmHandler` with `scaffold_fsm`.
  - Generates modular node-based state machine architecture: base `State` class with typed lifecycle hooks (`enter`, `exit`, `update`, `physics_update`, `handle_input`), and `StateMachine` controller managing transitions, history, and signal dispatch.
  - Built-in state presets: `enemy_ai` (Idle, Patrol, Chase, Attack, Hurt, Dead), `character` (Idle, Move, Jump, Fall), and `custom` (user-defined state script generation), with automatic hierarchy instantiation under target scene nodes.
- **Single-Call UI Theme Presets**: Added `apply_preset` to `theme_manage` (and GDScript `ThemeHandler`) supporting cohesive theme generation for `cyberpunk_neon`, `dark_modern`, `retro_pixel`, `fantasy_parchment`, and `clean_light`, styling Button states (normal, hover, pressed, disabled, focus), Panels, LineEdits, ProgressBars, Sliders, and Labels.
- **Multi-Channel Sound Effect Manager**: Added `scaffold_sound_manager` to `audio_manage` (and GDScript `AudioHandler`) to generate a `SoundManager` singleton with an `AudioStreamPlayer` pool (default 16 players) ensuring non-clipping sound effects, automatic pitch randomization (`pitch_variance`), volume controls, and 2D spatial playback.

## 5.0.16 (2026-09-21)

Autonomous game systems and engine scaffolding primitives: 2D/3D character controller scaffolding with physics and mouse capture, one-call input map presets, project display and rendering presets, 2D atmospheric lighting environment with radial torch illumination, singleton GameManager architecture with typed signals and scene switching, dedicated background music player scaffolding, and repository linter hygiene.

### Added

- **Character Controller and Movement Scaffolding**: Introduced `character_manage` tool and `CharacterHandler` with `scaffold_2d` and `scaffold_3d` operations.
  - `scaffold_2d`: Spawns `CharacterBody2D`, fitted `CollisionShape2D`, placeholder visuals, follow camera with trauma screen shake, and injects a production movement script with coyote time, jump buffering, floor snapping, and acceleration/friction curves for `platformer` and `topdown` genres.
  - `scaffold_3d`: Spawns `CharacterBody3D`, `CapsuleShape3D`, `CapsuleMesh`, and `Camera3D` (head mount or `SpringArm3D`) with mouse look capture, sprinting, jumping, gravity, and air control for `first_person` and `third_person` genres.
- **Input Map Presets**: Added `scaffold_preset` to `input_map_manage` (and GDScript `InputHandler`) to configure complete physical key bindings in one atomic call for `wasd_platformer`, `wasd_topdown`, `first_person`, and `driving`.
- **Project Display and Rendering Presets**: Added `apply_preset` to `project_manage` (and GDScript `ProjectHandler`) to atomically configure display viewport dimensions, window override sizes, stretch modes, and texture filtering for `pixel_art_2d`, `hd_2d`, `low_poly_3d`, and `cinematic_3d`.
- **2D Atmospheric Lighting Environment**: Added `environment_setup_2d` to `resource_manage` (and GDScript `EnvironmentHandler`) to configure ambient tinting via `CanvasModulate` (`dungeon`, `midnight`, `sunset`, `spooky`, `foggy`) and optionally attach a radial falloff `PointLight2D` torch with shadows to target characters.
- **Game Architecture Singleton Scaffolding**: Added `scaffold_game_manager` to `autoload_manage` (and GDScript `AutoloadHandler`) to generate and register a `GameManager` autoload singleton with typed signals (`score_changed`, `lives_changed`, `game_over`, `level_completed`), score/lives state, and scene reload/transition methods.
- **Dedicated Background Music Player**: Added `scaffold_music_player` to `audio_manage` (and GDScript `AudioHandler`) to create an `AudioStreamPlayer` routed to the `Music` bus with autoplay, volume control, and loop configuration.

## 5.0.15 (2026-09-21)

Production game scaffolding primitives and engine reliability hardening: Transport timeout scaling with non-fatal deferred retry, modal dialog detection, procedural chiptune audio synthesis, audio bus topology scaffolding, responsive UI screen scaffolding, 2D/3D navigation mesh and agent management, full 3D environment and lighting presets, 2D follow camera with trauma-based screen shake, and automated scene diagnostics.

### Added

- **Procedural Chiptune Audio Synthesizer**: Added `generate_procedural_sfx` to `audio_manage` (and GDScript `AudioHandler`) to synthesize 16-bit mono PCM WAV chiptune effects directly to disk for 8 core presets (`jump`, `coin`, `laser`, `hit`, `explosion`, `powerup`, `step`, `click`) with automatic editor filesystem reindexing.
- **Audio Bus Architecture Scaffolding**: Added `scaffold_buses` to `audio_manage` to initialize and configure standard `Master`, `Music`, `SFX`, and `UI` audio buses with custom dB attenuation in `AudioServer`.
- **Responsive UI Screen Scaffolding**: Added `scaffold_screen` to `ui_manage` (and GDScript `UIHandler`) to build production UI screen hierarchies under `CanvasLayer` (`main_menu`, `pause_menu`, `hud`, `game_over`, `dialog_box`) with dark translucent backdrops, centered card containers, header labels, separators, and interactive buttons under a single atomic UndoRedo action.
- **2D and 3D Navigation Primitives**: Introduced `navigation_manage` tool and `NavigationHandler` for 2D and 3D navigation mesh setup (`setup_region_2d`, `setup_region_3d`), agent attachment with collision avoidance (`attach_agent_2d`, `attach_agent_3d`), and synchronous/threaded in-editor polygon/mesh baking (`bake_2d`, `bake_3d`).
- **3D Environment and Lighting Presets**: Added `setup_environment_3d` to `resource_manage` (and GDScript `EnvironmentHandler`) to configure complete 3D scene lighting in one step, creating `WorldEnvironment` and `DirectionalLight3D` with sun angle, color, energy, shadows, tonemapping, and volumetric fog for presets: `daylight`, `sunset`, `dark_dungeon`, `neon_night`, `clear`.
- **2D Follow Camera with Trauma Screen Shake**: Added `scaffold_follow_2d` to `camera_manage` (and GDScript `CameraHandler`) providing smooth target following, zoom, bounds clamping, and built-in trauma-decay screen shake with an accessible `add_trauma(amount)` API.
- **Scene Doctor and Diagnostics**: Added `diagnose` to `scene_manage` (and GDScript `SceneHandler`) to run an automated scene audit detecting orphan collision objects, unassigned collision shape resources, non-uniform 2D collision scale artifacts, missing visual textures/meshes, and camera misconfigurations with actionable fix suggestions.

### Fixed

- **Transport Timeout and Circuit Breaker Hardening**: Implemented command-specific adaptive timeouts (up to 30s-60s) for heavy engine operations (`filesystem_scan`, `filesystem_download_asset`, `project_run`, `game_command`, `game_run_playtest_suite`, `scene_diagnose`, `navigation_bake_2d/3d`). Timeout occurrences on active sessions now raise retryable `DEFERRED_TIMEOUT` instead of recording failure counts against the 30-second circuit breaker lock.
- **Modal Dialog Detection**: Added modal window and dialog inspection in `editor_handler.gd`, surfacing `modal_dialog_active` in `get_editor_state` to prevent agent lockouts when confirmation dialogs are awaiting input.

## 5.0.14 (2026-09-19)

Autonomous 2D/3D development pipeline primitives: Alternative tile collision matrix synchronization, terrain bitmask scaffolder, multi-directional locomotion BlendSpace scaffolding, procedural particle presets, and in-engine automated playtest suite runner.

### Added

- **Alternative Tile Collision Matrix Synchronization**: Automatic cloning and rotation/flip transformation of 2D collision polygons onto alternative tiles when rotating or flipping tile cells (`rotate_cell`, `place_tile`, `flip_cell`, `import_matrix`). Prevents collisions from becoming misaligned or lost on rotated tiles.
- **Terrain Bitmask Scaffolder**: Added `scaffold_terrain_bitmasks` to `tileset_manage` (and GDScript `TileSetHandler`) supporting standard autotile templates (`kenney_3x3_minimal`, `rpgmaker_47`, `simple_box`) to stamp terrain peering bits automatically onto TileSet atlas sources.
- **8-Way Locomotion BlendSpace Generator**: Added `scaffold_locomotion_tree` to `animation_manage` (and GDScript `AnimationHandler`) to scaffold an `AnimationTree` with `AnimationNodeStateMachine` containing 2D directional blendspaces (`AnimationNodeBlendSpace2D`) for character locomotion states.
- **Procedural Particle Presets**: Added `spawn_preset_2d` to `particle_manage` (and GDScript `ParticleHandler`) to spawn pre-configured `CPUParticles2D` nodes with physics, color ramps, and emission curves for common effects (`dust_puff`, `sparks`, `smoke`, `ambient_leaves`) without external asset dependencies.
- **In-Engine Automated Playtest Runner**: Added `run_playtest_suite` to `game_manage` (and GDScript `game_helper.gd`) supporting sequential input holding, node property checks, GDScript expression evaluation, and waiting inside the live game loop at 60 FPS, returning detailed assertion logs.

### Fixed

- **Dev Environment uvx PyPI Lockout Prevention**: Enhanced `client_configurator.gd` to discover `.venv` in parent and sibling project directories and fallback to local repository root for `--from` during development, eliminating lockouts against unreleased PyPI versions.

## 5.0.13 (2026-09-19)

Comprehensive 2D/3D generation enhancements: Terrain autotiling parameter unification, asset download and nearest-neighbor ingestion, multi-state spritesheet scaffolding, virtual input simulation, and single-call batch entity instancing.

### Added

- **Spritesheet Animation Scaffolding**: Added `create_spritesheet_animation` to `animation_manage` (and GDScript `AnimationHandler`) allowing agents to configure `Sprite2D` (texture, hframes, vframes, nearest filter) and generate complete `AnimationPlayer` discrete keyframe tracks for multiple animation states in a single atomic UndoRedo call.
- **Batch Prop & Entity Spawning**: Added `instantiate_batch` to `scene_manage` and `node_manage` (and GDScript `SceneHandler`), enabling single-call bulk instancing of packed scenes with custom names, transforms (position, rotation, scale), and properties under an atomic UndoRedo transaction.
- **Virtual Input Simulation**: Added `simulate_input` to `game_manage` for frame-accurate action and key holding with automatic release after a specified duration, eliminating stuck keys during autonomous testing.
- **Asset Ingestion Pipeline**: Added `download_and_import` to `filesystem_manage` supporting `dest` path specification, automatic extraction, project-wide nearest-neighbor texture filtering configuration (`filter="nearest"`), and filesystem reimport/scan triggers.
- **Terrain Parameter Compatibility**: Added `terrain` parameter alias support alongside `terrain_id` for `tilemap_manage(op="paint_terrain")` in both Python handlers and GDScript `TileMapHandler`.

## 5.0.12 (2026-09-19)

Hotfix release resolving GDScript parse and type inference errors in the Godot plugin.

### Fixed

- **Animation Track Path Resolution**: Added `McpScenePath.path_relative_to()` static helper in `utils/scene_path.gd` to resolve `AnimationPlayer.root_node`-relative paths for `create_spritesheet_track`, and explicitly typed `rel_path: String` to eliminate compile errors.
- **TileSet Type Inference**: Explicitly typed loaded TileSet resource (`ts: TileSet = load(...) as TileSet`) and `tile_size: Vector2i` in `tileset_handler.gd` to eliminate GDScript 4 parse errors under strict type inference (`:=`).

## 5.0.11 (2026-09-19)


Lifecycle capability adoption reliability fix, single-editor auto-routing, and comprehensive 2D open-world, animation, and tileset authoring tools.

### Added

- **TileMap Open-World Tools**: Added `paint_terrain` (`TileMapLayer.set_cells_terrain_connect()`) for automated terrain autotiling, `import_matrix` for stamping large ASCII or 2D array tile layouts, and `scatter_props` for procedural scene prop scattering with random offset, rotation, and scaling.
- **2D Sprite Animation & State Machine Scaffolding**: Added `create_spritesheet_track` for discrete step keyframing on `Sprite2D` frame properties, `create_animated_sprite` to build `AnimatedSprite2D` nodes with sliced `SpriteFrames` resources, and `scaffold_state_machine` to construct `AnimationTree` nodes with root `AnimationNodeStateMachine` and automated transitions.
- **TileSet & Asset Authoring**: Added `create_from_texture` to automatically slice texture atlases into ready-to-use `TileSet` resources saved as `.tres`, and `create_collision_polygon` to generate custom collision shapes for tile physics layers.
- **Session Auto-Routing**: Single active editor instances automatically route tool calls in `SessionRegistry.get_active()` without requiring manual `session_activate` calls.
- **CC0 Asset Catalog Updates**: Updated asset URLs to verified 200 OK sources and added automatic 2D workspace viewport switching for 2D screenshots.

### Fixed

- **Server Lifecycle Adoption**: Fixed premature `launch_gone` dock blocking on Windows where process detachment or launch race conditions caused false-positive blockages. Capability probing now runs prior to process disposition checks and cleanly adopts compatible running servers within the proof deadline.
- **Dock Status Guard**: Guarded dock status snapshot requests against re-triggering server launches when WebSocket transport is already active.

## 5.0.10 (2026-09-18)

The dock no longer strands a user in a blocked state when two editors launch
at once: a server that loses the port-bind race is adopted instead of fought.

### Fixed

- When the launched server exits or changes identity before it proves (the
  symptom of a concurrent editor winning the port race), the lifecycle now
  automatically re-probes the endpoint on a bounded 1s/2s/4s/8s backoff and
  **adopts the compatible server that won the port** — never killing another
  editor's process and never spawning a second server. A free port still
  launches only our own server.
- The auto-recovery gives up after four attempts and leaves the dock blocked
  until a manual Restart; a genuine Restart at any time supersedes the
  scheduled timer. A fresh READY at any point earns a new budget, so a
  one-off race self-heals and a flapping one cannot loop forever.
- Incompatible version mismatches, proof timeouts, and genuine launch
  failures keep the dock's explicit authority exactly as before.

## 5.0.9 (2026-09-18)

Enabling the plugin now auto-configures every installed MCP client — Claude
Code, Codex, Antigravity, OpenCode and the others — one at a time, reliably.

### Added

- On its first ready transport per session, the plugin now auto-configures
  every installed, file-editable MCP client that isn't already pointing at
  the current server, writing the `godot-ai` attach entry for each
  (EditorSetting `godot_ai/auto_configure_clients`, default on; one-shot per
  session). Entries that already point at the server are never rewritten.
- The auto-configure sweep is strictly serialized: one client is configured
  at a time, and the queue only advances after the previous client's action
  completes — matching the dock's "Configure all" lock.

### Fixed

- The sweep no longer stalls after the first client. The completion handler
  advanced the queue only *after* presenting the result in the dock, so a
  dock presentation that crashed — the dock's `present_client_action_result`
  expected a bool prewarm flag while the handler passes the full result
  dictionary — aborted the handler and stranded the queue. The queue now
  advances before presentation, and the dock callback accepts the dictionary
  it is actually given.

## 5.0.8 (2026-09-18)

Maintenance release for Godot MCP. No runtime behavior changes.

### Changed

- Plugin version metadata (`plugin.cfg`), the dock version badges, and the
  packaged zip now report `5.0.8`, matching the GitHub release tag.
- Backfilled `CHANGELOG.md` entries for 5.0.3 through 5.0.7.

## 5.0.7 (2026-09-18)

Same-major-version server compatibility, clean port freeing, and robust dock
recovery.

### Changed

- The dock can adopt/reuse a server of the same major version instead of
  demanding a fresh instance.
- Ports are freed cleanly on server teardown.
- Dock recovery is robust when the server is active or reachable.

## 5.0.6 (2026-09-18)

### Fixed

- Clear the dock's blocked state when the server is active or reachable.

## 5.0.5 (2026-09-18)

### Added

- Precision TileMap placement.
- CC0 asset downloader and search.
- Direct editor placement directive.

## 5.0.4 (2026-09-18)

### Added

- Parity tools for ping, script validation, and filesystem management.
- README design overhaul.

## 5.0.3 (2026-09-18)

### Changed

- Unified Godot MCP dock without emojis and reliable server launch.

## 5.0.2 (2026-09-17)

Packaging and Asset Library readiness release for Godot MCP. No runtime
behavior changes.

### Changed

- Plugin version metadata (`plugin.cfg`) and the `godot-omni` server now all
  report `5.0.2`, matching the GitHub release tag.
- The release packaging script (`script/package_release.py`) takes the version
  as an argument instead of hardcoding it.
- Removed the duplicate `plugin/addons/*` tree from the repository; the
  root `addons/godot_ai` and `addons/godot_omni` folders are the single
  canonical source the release archives are built from.

### Asset Library

- `LICENSE` now carries a second copyright line for bebabin alongside the
  upstream Godot AI contributors attribution.
- `addons/godot_omni` now bundles its own `README.md` and `LICENSE` copies,
  matching `addons/godot_ai`.
- `.gitattributes` marks everything except `addons/`, `README.md`, `LICENSE`,
  and `docs/` as `export-ignore`, so an Asset Library download (which is built
  from the GitHub archive) contains a clean plugin archive instead of the
  whole repository.
- `addons/godot_ai/README.md` rewritten to describe this project instead of
  the upstream signed-archive flow.

### Fixed

- The `verify-signing` workflow referenced the removed `plugin/` tree; the
  embedded-key check now reads `addons/godot_ai/utils/update_manager.gd`.

## 4.1.0 (2026-09-11)

Plugin updates now activate inside the running editor, preserving open scenes,
unsaved changes, selection, and undo history. Updating from published 4.0.4
still restarts the editor once through its existing updater; later updates use
the new in-editor path. Published 3.2.5 can migrate through the new update
capsule without restarting the editor. Older AI clients may still need one
relaunch after migration.
[Compare v4.0.4...v4.1.0](https://github.com/hi-godot/godot-ai/compare/v4.0.4...v4.1.0).

### Fixed

- Fixed a native editor crash when an import runs while the Update confirmation
  is open. Godot's shared progress dialog survives plugin replacement and can
  be reused by the next filesystem scan.
- Updates wait for filesystem scans before replacing and enabling scripts,
  retain scripts needed by existing undo callbacks, and explain why an unsafe
  activation was refused.
- Startup and update recovery stay in a pending state until the server is
  ready. Genuine failures retain their error state and diagnostics.
- Windows process-inspection failures no longer masquerade as an exited
  process. Server ownership checks retain the evidence needed for recovery.
- Migration chooses an independent HTTP/WebSocket port pair. The dock's port
  picker updates the effective pair, including migrated settings, and also
  supports incompatible servers that cannot be reclaimed.
- Backup scans skip linked child directories, and Linux startup explains when
  required listener tools are missing.

### Known issue

- **Configure all** can report a client-configuration lock error when requests
  overlap. Configure clients individually, waiting for each operation to finish,
  and retry an affected client after the active operation completes. Tracked in
  [#1047](https://github.com/hi-godot/godot-ai/issues/1047).

## 4.0.4 (2026-09-09)

Updating with AI clients attached no longer means quitting and relaunching
them: from this version a client's `godot-ai attach` bridge keeps serving a
server of the same major version, and the restarted editor replaces the
server an old bridge left on the port by itself. Clients attached through
4.0.3 or earlier still need one last relaunch after this update. Also the
dock names each activation phase, a held WebSocket port is diagnosed before
launch, `physics_shape_generate` lands, and release qualification updates
with a real attached bridge.
[Compare v4.0.3...v4.0.4](https://github.com/hi-godot/godot-ai/compare/v4.0.3...v4.0.4).

### Added

- `resource_manage(op="physics_shape_generate")`: bulk-generate a
  `StaticBody3D` or `Area3D` sibling with a fitted `CollisionShape3D` (box,
  sphere, capsule or cylinder) for every `MeshInstance3D` path, as one undo
  action. Every path is validated before anything is written, and a deferred
  request re-validates each mesh again when its body is added, so a scene
  edited meanwhile fails the request instead of leaving a partial batch.
  Contributed by @michaltomczykowski in
  [#892](https://github.com/hi-godot/godot-ai/pull/892).

### Fixed

- The restarted editor's replacement of the server an attached bridge left on
  the port no longer loses the port to that bridge. The replacement server
  reports the moment it reaches its port wait and the occupant is killed only
  then, so a launch that spends seconds in uvx installing the new version no
  longer leaves the port free for the bridge to spawn a backend of the old
  version into (the 4.0.4 qualification's Ubuntu rows: three replacement
  attempts, each `HTTP port 8000 is already in use`). A bridge whose backend
  vanishes with the port free now also waits five seconds for a replacement
  to answer before spawning its own.
- The dock no longer looks frozen on "Downloading…" after the download has
  finished: activation now names each phase ("Verifying signed update…",
  "Staging the verified tree…", "Waiting for client workers…", "Activating
  verified update…") and lets the dock repaint before the phase's work runs.
- A server that refused to start now says why in the dock. The launch-failure
  message (`The launched process identity could not be captured…`) appends the
  server's own startup report, which two 4.0.3 reports had on disk unread:
  `WebSocket port 19630 is already in use by another process`.
- Moving the HTTP port alone no longer lands the next launch on a WebSocket
  port the previous server still holds: the lifecycle preflights the WebSocket
  port before launching and names `godot_ai/ws_port`, and the dock's port picker
  moves both ports, keeping whichever one is free.
- `Port N is occupied by another process` now says why a godot-ai record for
  that port did not authenticate the occupant (a probe timeout, a different
  instance, a non-godot-ai listener), so the report is actionable.
- After an update the restarted plugin replaces any older server of its
  major version that an attach bridge left on the port, not only the exact
  version it superseded, and its post-update status probe waits 3 s instead
  of 800 ms so a backend still settling on the port is not reported as
  "held by another process" with nothing replacing it.
- The post-update banner and log line say "AI clients keep working" when the
  clients were attached through 4.0.4 or newer (their bridges follow the new
  server), and keep telling the user to quit and relaunch only for bridges
  that predate it.

### Changed

- The `godot-ai attach` bridge keeps serving a server of the same **major**
  version instead of requiring the exact package version. Updating the plugin
  no longer requires quitting and relaunching every attached AI client: the
  restarted editor's server is one patch or minor ahead of the client's bridge
  pin, the bridge re-validates on every request and follows the new server
  instance. The attach protocol version, ports and excluded domains are still
  gated exactly. Bridges from 4.0.3 and earlier still refuse a newer server,
  so the first update onto this version needs one last relaunch.
- Release qualification's real-editor A-to-B update now runs with a real
  `godot-ai attach` bridge attached through the update, and passes only when
  that same bridge process serves the updated editor afterwards, so the gate
  measures the workflow users actually run.

## 4.0.3 (2026-09-08)

Stabilizes the v4 line on Windows and Linux after the 3.x crossing: the
private capability directory the account could not use, the post-update
client barrier, servers left behind by a client's old 3.x bridge, the
closed-editor recovery installer, the Reload Plugin crash, and the updater's
lock. Quit and relaunch AI clients that were connected during the update.
[Compare v4.0.2...v4.0.3](https://github.com/hi-godot/godot-ai/compare/v4.0.2...v4.0.3).

### Fixed

- `editor_reload_plugin` (and the dock's Reload) gave up after 5 s when the
  editor was still scanning or importing, left the plugin unchanged with only
  an editor-log error, and the calling AI client then waited out the server's
  90 s reconnect budget for a replacement session that never came. The
  reload now waits up to 60 s for its filesystem scan.
- **OpenCode:** Configure wrote only `opencode.json` while OpenCode merges
  it with `opencode.jsonc`, the latter winning per key, so a stale
  `godot-ai` entry in an existing `opencode.jsonc` kept overriding the new
  one. The descriptor now declares that merge order: Configure updates the
  effective last definition, status verifies it, Remove clears both
  ([#1011](https://github.com/hi-godot/godot-ai/issues/1011)).
- A Godot AI 3.x server left on the port by an AI client whose bridge
  attached before the update was reported as "held by another process". The
  lifecycle now performs one untrusted, tokenless status read solely to word
  the block: it names the pre-v4 server, tells the user to quit and relaunch
  that client, and re-probes slowly for about three and a half minutes so
  the editor comes up green once the old server's lease and idle backstop
  run out. The read grants no adoption, replacement or kill authority. The
  dock and the migration guide now say "quit and relaunch" rather than
  "restart": Claude Desktop keeps its MCP configuration in memory and
  respawns the old bridge until the application itself is relaunched.
- After an update, a client entry the migration could not prove as
  "what Configure wrote before the update" (a project `.mcp.json` with a
  v3 `type: http` entry, an unreadable file) blocked the server with
  `<client> has non-version configuration drift; automatic migration
  refused` and a Retry that failed the same way. The entry is still never
  rewritten (#890), but it no longer holds the server: it is left
  unchanged, named in the completion banner with a Configure hint, and
  startup continues. While an update brings the server back the dock now
  reads `Finishing update — starting server…` instead of a red
  `Connection blocked`
  startup continues
- **Closed-editor recovery installer** (`script/v4-release install`, the
  #999 procedure): on Windows it treated every update-lock holder as dead
  when `psutil` was not installed, which the published command never
  installs, so a live editor's lock was replaced instead of refused; the
  check now asks the kernel directly and needs no third-party module. A
  recovery over an existing 4.x tree also records
  `replace_owned_mismatches`, so the plugin's first start may repin every
  owned client entry that launches Godot AI, whatever the live tree's
  version, instead of refusing startup over a leftover v3-shaped entry
  ([#999](https://github.com/hi-godot/godot-ai/issues/999)).
- **Windows:** the server launched to replace an older godot-ai backend gave
  up waiting for the port after 5 s, before the plugin had finished proving
  the new process and killing the old one (each identity probe is a
  PowerShell start), so a post-update replacement could loop on `The launched
  process identity could not be captured`. The replacement now waits 15 s,
  and that message names the process, whether it is still alive, and which
  check refused it on each attempt.
- **Windows:** the server created its private capability directory with
  `mode=0o700`, which CPython turns into a DACL of SYSTEM, Administrators and
  OWNER RIGHTS alone. A directory first created by an elevated process is
  then owned by Administrators, and the user's own unelevated editor, server
  and `godot-ai attach` bridge can never read or write it: the dock showed
  `The managed server proof timed out at capability_record` and the bridge
  reported `PORT_OCCUPIED` for a healthy backend. The directory now inherits
  the per-user `%LOCALAPPDATA%` permissions; the plugin probes it before
  spawning and the bridge checks it before blaming a foreign process, and
  both name the directory and the elevated `Remove-Item` repair when the
  account cannot use it
  ([#988](https://github.com/hi-godot/godot-ai/issues/988)).
- A plugin-spawned server that fails before publishing its capability record
  now writes the failure to a startup report (`--startup-report`, beside the
  pid file) and the dock appends it to the proof failure, so a port in use, an
  unwritable directory or a crashed import is named instead of a bare
  `proof timed out at capability_record`
  ([#1012](https://github.com/hi-godot/godot-ai/issues/1012)).
- `camera_create` / `camera_configure` / `camera_apply_preset` with
  `make_current` on a **Camera2D** could leave the camera not current while
  the response and `camera_get` said it was. Godot's `Camera2D.make_current()`
  dispatches through a scene-tree group call that silently skips a node
  allocated at the address of a node removed and freed earlier in the same
  editor frame, which happens after undo-history trimming, `free()`, or an
  editor panel rebuild. The handler now detects the dropped call and applies
  the same viewport update directly. This was the "engine-state lag" behind
  the long-running camera test flake (#140, #278, #301, #316); the retry and
  sleep loops written for it are gone.
- **Bazzite / Fedora Atomic:** the server exited before publishing its
  capability record because `/home` is a symbolic link to `/var/home` on
  ostree systems and 4.0.x refused every link in a capability path. The server
  now follows a link when it is root-owned and sits in a root-owned directory
  that other accounts cannot write, which is exactly the ostree layout. The
  plugin, which cannot see file ownership, follows a link only below a
  directory closed to group and other writes. Every other link still fails
  closed on both sides, and the record file itself is never followed. The
  `GODOT_AI_CAPABILITY_DIR` workaround is no longer needed there
  ([#993](https://github.com/hi-godot/godot-ai/issues/993), reported again in
  [#989](https://github.com/hi-godot/godot-ai/issues/989)).
- The dock's **Reload Plugin** button no longer crashes the editor
  ([#1000](https://github.com/hi-godot/godot-ai/pull/1000)).
- After an in-session update the dock's Update button is an action again and
  re-arms for a newer release without an editor restart
  ([#1002](https://github.com/hi-godot/godot-ai/pull/1002)).
- A failed download releases the update lock
  ([#1001](https://github.com/hi-godot/godot-ai/pull/1001)).

### Changed

- Documented the supported way to connect an agent that runs in a container,
  in WSL2, or on another machine: the `godot-ai attach` bridge launched on the
  editor machine over SSH, with the Docker Desktop, Docker Engine, and WSL2
  host names ([#1008](https://github.com/hi-godot/godot-ai/issues/1008);
  a first-class remote mode is tracked in
  [#1009](https://github.com/hi-godot/godot-ai/issues/1009)).

## 4.0.2 (2026-09-07)

Fixes the in-editor updater's download. Nothing else changed.
[Compare v4.0.1...v4.0.2](https://github.com/hi-godot/godot-ai/compare/v4.0.1...v4.0.2).

### Fixed

- The dock's **Update** failed with `download failed (302)` on Windows, macOS,
  and Linux. Two independent causes: with `max_redirects = 0`, Godot's
  `HTTPRequest` reports `RESULT_REDIRECT_LIMIT_REACHED` for GitHub's first
  redirect instead of a success carrying a 3xx code, so the manual redirect
  branch was unreachable; and GitHub's release-asset CDN now uses a
  `/github-production-release-asset/<repository id>/...` path that the trusted
  path check rejected. The updater now treats that result as a redirect and
  pins the current CDN namespace to this repository's ID, keeping the
  destination validation and redirect limit
  ([#997](https://github.com/hi-godot/godot-ai/pull/997); reported in
  [#998](https://github.com/hi-godot/godot-ai/issues/998) and
  [#989](https://github.com/hi-godot/godot-ai/issues/989)).
- The private origin used by release qualification issues a real redirect
  before serving bytes, so every A-to-B update test now exercises this path.

### Upgrading

- **From 3.2.5:** click **Update** with Godot 4.7 or newer. You go directly to
  4.0.2.
- **From 4.0.0 or 4.0.1:** those versions cannot download this fix with their
  own Update button. Follow the one-time recovery in
  [#999](https://github.com/hi-godot/godot-ai/issues/999) (also documented in
  [docs/releasing.md](docs/releasing.md#recovering-the-400--401-http-302-download-failure)).
  Afterwards the Update button works again.

## 4.0.1 (2026-09-07)

[Compare v4.0.0...v4.0.1](https://github.com/hi-godot/godot-ai/compare/v4.0.0...v4.0.1).

### Fixed

- After the first ordinary editor start following the v4 migration, client
  rows stayed on **Installing…** or **Checking…**, **Configure all** was greyed
  out, and `client_manage(op="status")` timed out. The client job owner's
  `_ready` ran after `activate()` and switched its polling off
  ([#991](https://github.com/hi-godot/godot-ai/pull/991) by @Noniv; closes
  [#990](https://github.com/hi-godot/godot-ai/issues/990), and the stuck-dock
  half of [#989](https://github.com/hi-godot/godot-ai/issues/989)).

### Changed

- The README documents the Bazzite / Fedora Atomic capability-directory
  workaround ([#995](https://github.com/hi-godot/godot-ai/pull/995); closes
  [#993](https://github.com/hi-godot/godot-ai/issues/993)).
- Release tooling resumes a hidden draft release and waits for PyPI's index
  ([#987](https://github.com/hi-godot/godot-ai/pull/987)); Windows client
  configuration is tested across editor restarts
  ([#994](https://github.com/hi-godot/godot-ai/pull/994)).

4.0.1 shares the download bug fixed in 4.0.2, so it could not be installed
from 4.0.0 through the dock.

## 4.0.0 (2026-09-07)

Godot AI 4 is a breaking release built around one signed add-on tree, one
authenticated transport, and an updater that replaces the whole tree or
nothing. Migration guide: [docs/v4-migration.md](docs/v4-migration.md).
[Compare v3.2.4...v4.0.0](https://github.com/hi-godot/godot-ai/compare/v3.2.4...v4.0.0)
(3.2.5 was cut from the `release/v3` branch, so the comparison starts at the
last shared tag).

### Requirements and compatibility (breaking)

- **Godot 4.7 or newer.** Godot 4.5 and 4.6 load the migration bridge only far
  enough to report the requirement; below the floor the bridge restores the
  previous 3.2.5 add-on instead of leaving a dead plugin. Upgrade Godot, reopen
  the project, and retry the migration
  ([#943](https://github.com/hi-godot/godot-ai/pull/943),
  [#968](https://github.com/hi-godot/godot-ai/pull/968)).
- **Python 3.11 through 3.14** for the server, provided through `uv`. Every
  runtime dependency is an exact pin (FastMCP 3.4.7, MCP 1.29.1, websockets
  17.1, Uvicorn 0.52.4, Starlette 1.6.0, Pydantic 2.13.5, httpx 0.28.1) and
  the pins are checked again when the server starts. Dependency upgrades are
  reviewed release changes ([#943](https://github.com/hi-godot/godot-ai/pull/943)).
- **Clients connect through `godot-ai attach` over stdio.** A bare
  `http://127.0.0.1:8000/mcp` entry can no longer authenticate. Use the dock's
  **Configure**, or the **Run this manually** command it shows
  ([#943](https://github.com/hi-godot/godot-ai/pull/943)).
- **v3 and v4 do not interoperate.** A v3 plugin against a v4 server, or the
  reverse, fails closed; there is no tokenless or legacy-handshake fallback
  ([#943](https://github.com/hi-godot/godot-ai/pull/943)).
- **Cherry Studio is no longer supported.** Its servers live in an internal
  database Godot AI cannot safely edit; remove stale v3 entries in Cherry
  Studio itself. **Zed** is manual-edit only, and the dock now reads Zed's
  commented `settings.json` for status instead of reporting a parse error
  ([#954](https://github.com/hi-godot/godot-ai/pull/954); closes
  [#914](https://github.com/hi-godot/godot-ai/issues/914)).
- **Distribution is GitHub Releases only.** The Godot Asset Store and Asset
  Library listings stay on the last v3 release. A stable release publishes six
  assets: the canonical `godot-ai-v4-plugin.zip` with its signed manifest and
  signature, and the legacy-named `godot-ai-plugin.zip` triple, which is now
  the v3-to-v4 migration capsule rather than an installable add-on. Never
  extract release files over an existing `addons/godot_ai/`
  ([#943](https://github.com/hi-godot/godot-ai/pull/943),
  [#949](https://github.com/hi-godot/godot-ai/pull/949)).

### Update and migration

- **One-click migration from 3.2.5.** Click **Update**; Godot restarts once,
  owned client entries are repinned, and the matching v4 server starts.
  Nothing to download, verify, or edit by hand
  ([#943](https://github.com/hi-godot/godot-ai/pull/943),
  [#968](https://github.com/hi-godot/godot-ai/pull/968)).
- **New in-editor updater.** The release manifest is RSA-4096 signed and binds
  repository, channel, tag, version, source commit, archive hash, and every
  file's size and hash. The updater verifies it, stages the tree under
  `addons/.godot_ai_update/stage/`, swaps the live add-on with two renames,
  restarts the editor, and hashes the new tree again before it runs. The
  previous add-on is kept at `addons/.godot_ai_update/backup/<old version>/`
  until the next successful update. The outcome is recorded in
  `addons/.godot_ai_update/pending.json` as `success`, `rolled_back`, or
  `repair_required`; nothing needs deleting by hand to make progress
  ([#968](https://github.com/hi-godot/godot-ai/pull/968);
  [docs/self-update.md](docs/self-update.md)).
- An update refuses before touching anything when another editor is using the
  same add-on, and it never overlays files into the live tree.
- After an update, the plugin replaces a leftover server of the version it
  just updated from and asks you to restart AI clients that were connected
  during the update ([#968](https://github.com/hi-godot/godot-ai/pull/968)).
- Client entries under the `godot-ai` name that launch something other than
  Godot AI are reported in the editor output, not rewritten; ownership is
  matched on exact launch tokens
  ([#971](https://github.com/hi-godot/godot-ai/pull/971),
  [#973](https://github.com/hi-godot/godot-ai/pull/973),
  [#975](https://github.com/hi-godot/godot-ai/pull/975)).
- **Gated publication.** Only bytes that passed the cross-platform
  qualification run, including a real-editor update on Linux, macOS, and
  Windows, can be signed and published, behind a required reviewer
  ([#949](https://github.com/hi-godot/godot-ai/pull/949)).
- `script/v4-release install` performs the same verify, stage, swap sequence
  with the editor closed, for qualification and recovery.

### Security and transport

- **Both local hops are authenticated.** The MCP HTTP endpoint requires a
  bearer capability and the editor WebSocket a separate 32-byte capability;
  neither accepts a tokenless connection. Capabilities are generated per
  server instance and published through a private, owner-only record under
  `~/.config/godot-ai/capabilities` (Linux),
  `~/Library/Application Support/godot-ai/capabilities` (macOS), or
  `%LOCALAPPDATA%\godot-ai\capabilities` (Windows). `GODOT_AI_CAPABILITY_DIR`
  overrides the location on Linux and macOS
  ([#943](https://github.com/hi-godot/godot-ai/pull/943)).
- Connection, body, frame, and session budgets are bounded. Duplicate JSON
  keys, replayed nonces, and v3 protocol frames are rejected.
- Capability paths that pass through a symbolic link are refused. On Bazzite
  and other Fedora Atomic desktops, where `/home` links to `/var/home`, follow
  the README workaround ([#993](https://github.com/hi-godot/godot-ai/issues/993)).
- The `uvx` launch is isolated (`--isolated --no-config --no-env-file
  --no-sources --no-build`) and names the public PyPI index explicitly, so an
  ambient alternate index or uv configuration cannot change what runs.
- **Telemetry opt-out reaches adopted servers.** Unchecking telemetry now
  sends a one-way `telemetry_opt_out` event over the authenticated WebSocket,
  so a server the plugin adopted rather than spawned stops sending too, and
  `/godot-ai/status` reports what the running server will actually send
  ([#955](https://github.com/hi-godot/godot-ai/pull/955); closes
  [#913](https://github.com/hi-godot/godot-ai/issues/913)).

### Tools

- `game_manage` gains `suspend`, `resume`, `next_frame`, and `debug_status`,
  driven through Godot's native debugger: the Embedded Game View when it is
  available, the debugger session otherwise
  ([#953](https://github.com/hi-godot/godot-ai/pull/953) by @quakquak86;
  closes [#939](https://github.com/hi-godot/godot-ai/issues/939)).
- `test_run` and `test_manage(op="results_get")` return `cache_warning` when
  preloaded GDScript may be stale after an edit in the same editor. Restart
  the editor before validating dependency changes
  ([#985](https://github.com/hi-godot/godot-ai/pull/985); closes
  [#938](https://github.com/hi-godot/godot-ai/issues/938)).
- Numeric strings such as `"4.0"` are coerced to floats across node, camera,
  material, animation, and audio value handlers, for clients that stringify
  float arguments ([#969](https://github.com/hi-godot/godot-ai/pull/969) by
  @robbe1912; closes [#964](https://github.com/hi-godot/godot-ai/issues/964)).
- The tool surface is 46 tools: 19 named tools plus 27 `<domain>_manage`
  rollups ([docs/TOOLS.md](docs/TOOLS.md)).

### Clients

- CodeBuddy IDE is configured automatically through `~/.codebuddy/mcp.json`
  ([#983](https://github.com/hi-godot/godot-ai/pull/983); closes
  [#941](https://github.com/hi-godot/godot-ai/issues/941)).

### Reliability

- Losing the authenticated editor-server session is no longer terminal. The
  plugin re-probes with a 1, 2, 4, 8, 16 second backoff, five attempts per
  outage, before asking for **Restart**
  ([#982](https://github.com/hi-godot/godot-ai/pull/982); closes
  [#962](https://github.com/hi-godot/godot-ai/issues/962)).
- Concurrent `godot-ai attach` clients on Windows no longer fail on the
  startup lock race ([#986](https://github.com/hi-godot/godot-ai/pull/986)).
- Also in 4.0.0, and already shipped in 3.2.5: an already-loaded GDScript is
  refreshed after script writes
  ([#944](https://github.com/hi-godot/godot-ai/pull/944)); a UTF-8 BOM
  survives a token-preserving Remove
  ([#956](https://github.com/hi-godot/godot-ai/pull/956)); the editor
  WebSocket keepalive deadline is wider
  ([#961](https://github.com/hi-godot/godot-ai/pull/961)); the Windows
  `test_project` junction repair never deletes a real plugin copy
  ([#947](https://github.com/hi-godot/godot-ai/pull/947)); the version-check
  refcount cycle and descendant ownership on reparent and duplicate undo are
  fixed.

### Known issues in 4.0.x

- 4.0.0 and 4.0.1 cannot download an update (`download failed (302)`). Fixed
  in 4.0.2; recovery in [#999](https://github.com/hi-godot/godot-ai/issues/999).
- Bazzite / Fedora Atomic: the server exits before publishing capabilities
  because `/home` is a symbolic link
  ([#993](https://github.com/hi-godot/godot-ai/issues/993)); the README
  documents the `GODOT_AI_CAPABILITY_DIR` workaround.
- The dock's **Reload Plugin** button can crash the editor. Fixed on `main` by
  [#1000](https://github.com/hi-godot/godot-ai/pull/1000); ships in the next
  release.
- After an in-session update the dock's Update button reads **Update
  complete** and cannot take a newer release until the editor restarts. Fixed
  on `main` by [#1002](https://github.com/hi-godot/godot-ai/pull/1002); ships
  in the next release.
- A failed download leaves the update lock in place; clicking Update again in
  the same editor still works. Fixed on `main` by
  [#1001](https://github.com/hi-godot/godot-ai/pull/1001); ships in the next
  release.
- The limits accepted for 4.0.0 after independent review are recorded in
  [docs/self-update.md](docs/self-update.md#known-limits-400).

## Earlier releases

3.x release notes are on the
[GitHub Releases](https://github.com/hi-godot/godot-ai/releases) pages.
