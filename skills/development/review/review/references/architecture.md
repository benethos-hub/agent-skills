# Architecture rules for a project without its own

The project's own rules always come first: an architecture document, the instruction files, a test that checks imports. Use the rules below only where the project says nothing. A finding drawn from them is a proposal with its reason, not a violation, since the project never agreed to them.

The rules come from a service that was built to them and checks them with a test on every run. They hold for any language. The words "package" and "module" stand for whatever the language groups code by.

## 1. Layers

Three layers, and dependencies point down only:

```text
 presentation   input and output: requests, pages, commands. Knows who is calling.
 logic          decides: rules, rights, workflows. Knows no transport and no storage.
 data           reads and writes: storage, files, other systems. Decides nothing.
```

- **Cross-cutting modules** such as configuration, errors and small helpers are read by every layer and depend on none.
- **The assembly** is the one place that may reach everywhere. It decides which implementation is used, from the settings, and hands it in. Code that uses an implementation never picks it itself. That is also how tests swap in fakes.
- **No transport in the logic.** Nothing below the presentation knows a status code or raises an error of the web framework. The logic raises the project's own errors, and the presentation maps each to its answer.
- **No decisions in the data layer.** It reads and writes, it does not judge.
- **A rule is checked in one place.** When two front ends, such as an API and a user interface, call the same logic, rights are checked in the logic. A check in each front end is built twice, and one of the two drifts.

## 2. Packages

- **Cut by subject or by kind**, such as `accounts` or `storage`, never by pattern, such as `services` or `utils`. A package holds what belongs together, not what is alike.
- **Named for what it is about.** A module is not named like its package. `sync/sync` says nothing.
- **Used through its public interface.** Other packages import what it exports, never a module inside it. So it can split or merge its modules without its callers noticing. Tests may reach inside.
- **The entry of a package exports, it does not implement.** Code longer than a few lines lives in a module.
- **No cycles.** What two packages both need goes to a package below both, or is handed in by the assembly.
- **Packages stand in lines.** Each imports only lines below its own. Draw the lines once, so a new import can be checked against them.

## 3. Where does it go?

| Adding | It goes to |
|---|---|
| an endpoint, a page, a command | the presentation, one module per resource or command |
| the check of who is calling | the presentation, in one place. Nothing else there decides |
| a decision, a rule, a right | the logic, in the package of its subject |
| a type several layers pass around | a models package low down, one module per subject |
| a record that is stored | its model, a storage interface, the implementations behind it, a migration |
| a connection to another system | the data layer, behind an interface, reached through a registry or a factory |
| a third-party library | one wrapper module in the layer that needs it, translating into the project's types and errors |
| an error | the central errors module. The presentation maps it to its answer |
| a setting | the central configuration, with its default and an example line |
| a helper one layer needs | that layer, beside its caller |
| a helper that knows no layer | the shared helpers, only without I/O and without state. Otherwise it belongs to a layer |
| a helper several programs need | a shared package below all of them |

When none of these fits, the seam is missing. Add the seam first, then the code.

## 4. Libraries and seams

- **One library, one home.** Each third-party library, the standard library's I/O included, is imported in one module, or one package for a framework. When it is needed elsewhere, its wrapper is extended.
- **Our interface, not theirs.** Code depends on an interface the project defines, never on a library's types. A library's objects, errors and quirks do not cross its wrapper.
- **Translate at the edge.** Data from outside is read into the project's types once, where it enters. Failures become the project's errors there.
- **One technology, one module.** Swapping a library, the database or the web framework should mean rewriting one module. A change that has to touch several layers to swap one technology says the seam is in the wrong place. That is a structure finding.
- **Tests use the seams.** Fakes are plugged in at an interface, not patched deep inside a library.

## 5. Values

- **Types at boundaries.** What crosses a boundary has a declared shape, checked where it enters.
- **Values inside a layer do not change** once made. A record with named fields, not a tuple or a loose dictionary.
- **Ids are opaque** to callers. No caller takes one apart.
- **Secrets are wrapped** the moment they are read, so they cannot be printed by accident.

## 6. A rule no test checks is a wish

When the project agrees to a rule, propose a test that checks it on every run: the direction of imports, the homes of libraries, the absence of cycles, size limits for modules and classes. Such a test is a finding of its own, in the structure package.
