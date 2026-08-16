# Source: https://engineering.hmn.md/how-we-work/process/agile/

# Agile & Scrum

Projects at Human Made follow an agile approach, typically following the Scrum framework. This helps us move faster and work together better as a team, while ensuring engineers can get work done without constantly being blocked.

Agile and Scrum approaches use some specific terminology and processes that you should get to know. While it might seem like a lot to learn, most of the time this is just putting better names on things you’re already doing, as well as systematising things to avoid guesswork. The process is here to help the whole team produce great products, and should help you be more effective and productive in your job.

One of the big advantages of Scrum for engineers is that it’s self-directed: the Scrum Master doesn’t tell you what to do. Once the whole team has decided on the direction you get to work together on delivery and are empowered to do it in the way you see fit.

With that great freedom though comes equally great responsibility.

When you are on a Scrum team, we trust that:

* You have the power to solve the problem – issues won’t have detailed specs about HOW to build what we need, we’ll leave that to you and the team.
* You will commit to the whole goal of the sprint.
* You will do all in your power to meet your commitment.
* You will work together to meet the commitment.
* You will communicate if unforeseen circumstances alter what you’re able to deliver.

## “Who”: The Participants [#](#who-the-participants)

Scrum is based around a small group of cross-functional team members working to deliver a result. They have specific, named roles in the scope of the project:

* **Product Owner** (Key stakeholder)
* **Scrum Master** (Facilitator, typically HM project manager)
* **Development Team**
* **Business Analyst**
* **Stakeholders** (Other people on the business side)

### Product Owner [#](#product-owner)

The Product Owner (PO) operates as the key stakeholder on the project. They may actually be finally responsible, but equally may report to Product Managers, other stakeholders or Business Owners.

It’s generally preferable to have someone client-side working as the PO, as they better understand the desired product. They are responsible for knowing the product inside and out, knowing how it will be used, knowing what and who it is for, and where it will deliver the value to the business. The PO will identify and articulate the features, and prioritise them.

The Product Owner role is typically filled by someone on the client-side, but may be filled by the project manager, or for internal projects, by the lead engineer.

### Scrum Master [#](#scrum-master)

The Scrum Master is the facilitator. They provide the interface between the PO and the Development Team, running interference, clearing blockers, and generally supporting the Dev Team with whatever they need to get on with the job without interruption.

The Scrum Master role is typically filled in projects by project managers, but may be filled in smaller or internal projects by the lead engineer.

### Development Team [#](#development-team)

The Development Team is the team responsible for building the product. They are a group of dedicated individuals capable of working across disciplines, who are team-focused, and results-oriented participants in the process.

The Development Team is a cross-functional team of engineers, including senior engineers and a lead engineer, designers, QA testers, and any other roles necessary to build the product.

### Business Analyst [#](#business-analyst)

A business analyst can be helpful to the Product Owner by supporting them with contributing to the product definition, gathering requirements, defining issues and outlining things like Acceptance Criteria. Particularly useful to support the PO on large, detailed projects with many moving parts.

### Stakeholders [#](#stakeholders)

All of the people on the business side who have a responsibility towards the project.

Stakeholders can include Technical Officers, Business Owners, Product Managers, Marketing Managers, or others.

## “What”: Scrum Project Lifecycle [#](#what-scrum-project-lifecycle)

Scrum projects follow a specific lifecycle from project conception through to delivery. As an engineer, you’ll be involved in all of these steps to some degree.

Projects initially start with a project idea, which then becomes a high-level product specification. This is then refined during a workshop down to an initial backlog of issues.

Once development has started, the project revolves around Sprints and their associated events. These are typically two to four week long blocks of development time, and this repeats until the backlog is complete (that is, until the project is complete).

### Product Conception [#](#product-conception)

*Goal: Resolve some perceived business need, gap in the market, or problem.*

### Spec Outline Creation [#](#spec-outline-creation)

From the original product idea, a Product Specification is created. This is a high-level overview based on business logic/needs.

*Goal: Define and articulate the problem to get stakeholder buy in and commitment*

### Product Refinement Workshop [#](#product-refinement-workshop)

A product refinement workshop is held with the Product Owner, Scrum Master, and Development Team. This workshop is used to build an initial Product Backlog.

The Product Backlog is an ordered list of all the features that need to be included in the project, it is a dynamic list, responsive to the evolving needs of the project.

* User research conducted to identify the problems being solved.
* User stories written to help frame the features.
* Backlog created from the user stories.

*Goal: A Refined backlog with the backbone of the product in place*

### Systems and Processes Agreement [#](#systems-and-processes-agreement)

The Product Owner, Scrum Master, and Lead Developer (and any other stakeholders) discuss and agree on:

* Deployment Strategy
* Issue Tracking Tools and Processes
* Definition of Done
* Sprint Length
* Meeting Schedule

The Definition of “Done” is an important step which makes clear to everyone involved exactly what an issue being “Done” involves. This needs to be defined and understood before development can begin. For example, it might involve:

* Code review has passed
* Functional tests have been created and automated
* User Story has been tested and checked against the Acceptance Criteria for the issue
* Issues have been created to address Technical Debt
* Feature has been deployed to production

*Goal: Set the parameters around which the development process will run*

### Backlog Refinement [#](#backlog-refinement)

Before planning a Sprint, the Product Backlog undergoes backlog refinement. During refinement, issues are prioritised, Acceptance Criteria is established, and issues are estimated.

* Definition of top priority issues that includes adding Acceptance Criteria (the items against which the issue will be tested).
* Estimation initiated, using tools to assist in relative estimation and assigning story points e.g. Planning poker.

Story points are used to estimate task size. Using a few cards out of a standard deck, or a specialized deck for Scrum, the dev team can use the Fibonacci sequence to create points of comparison (typically 3, 5, 8, 13, 21). The goal is not to estimate time, but task size relative to other tasks.

(There are also apps for this, allowing members to reveal their estimates together and then discuss, rather than be influenced by one person’s initial assessment.)

An Acceptance Criteria is created for each issue. This is an issue-specific criteria needed to consider the issue complete, and is combined with the project-wide Definition of “Done”.

*Goal: Give the development team visibility on the work that needs doing, outline expectations, and allow the Dev Team to ask questions to facilitate understanding of issue needs, estimate issues to gauge the anticipated workload.*

### Sprint Planning [#](#sprint-planning)

Well before a sprint begins, a Sprint Backlog is created. The Sprint Backlog is the smaller list of stories taken from the top of the Product Backlog that has been committed to by the Development Team and designated to be completed in the Sprint.

Sprint planning usually happens at least two sprints ahead of time.

This includes:

* Capacity Update
* Issue Review
* Velocity Prediction
* Team Buy In
* Team Commitment/Agreement

*Goal: to plan work for the upcoming sprint/s, outline priorities, account for capacity changes, and commit to deliver*

### Sprint [#](#sprint)

A sprint (or iteration) is the basic unit for development. It’s timeboxed, which means it has a restricted unit of time and can act as a subproject within the wider development project.

The parts of a sprint are:

* Get to Work
  + Build
  + Test
  + Review
  + Release
* Communicate Issues
* Risk Management
* Complete

A typical sprint is either two or four weeks long.

*Goal: To complete work committed to in Sprint Planning, to deliver completed, working code.*

### Standup [#](#standup)

The daily rhythmn of a sprint includes a regular, short, check in meeting called Standup. In this meeting, led by the Scrum Master, the team report on the following 3 questions.

* What did you do since last Standup?
* What will you be working on today?
* Are there any blockers you need help with?

*Goal: To surface problems and blockers early so the team can work together quickly to solve them.*

### Sprint Review [#](#sprint-review)

The Sprint Review (sometimes called a showcase) happens at the end of a sprint and is used to demonstrate to stakeholders what has been completed in the most recent sprint.

* Measure against the Definition of “Done”
* Showcase completed Work
* Review/Report on Burn-down and Velocity

*Goal: Demonstrate work that has met the definition of done. Review what was committed to, measure that against what was completed, look ahead to the next sprint goal*

### Sprint Retrospective [#](#sprint-retrospective)

The Sprint Retrospective happens once per sprint and is an opportunity for the entire team to come together and evaluate what went well and what needs improvement. The aim is to produce a set of action items for the team to help them increase the efficiency of succeeding sprints.

* Celebrate Success
* Review Failures
* Resolve to improve together

*Goal: Review the Previous Sprint, evaluate successes and failures, outline actions required to improve results for the next sprint.*

### Repeat! [#](#repeat)

The Backlog Refinement, Sprint Planning, Sprint, Sprint Review, and Sprint Retrospective steps are repeated constantly until the project is complete; that is, until the backlog is empty.

## “Why/How”: Rationale and Practice [#](#whyhow-rationale-and-practice)

So the above outlines the framework and backbone, but it doesn’t cover wholly the actual, practical application.

### Communication [#](#communication)

One of the keys to the Scrum process is communication and transparency. This happens through frequent communication, often in the form of meetings. This communication provides mechanisms for the Prduct Owner and Development Team to discuss, plan and execute the development of working code. It also provides a mechanism for learning and improving and iterating on previous work.

Before the first sprint, an initial Backlog Refinement is held, generating enough issues for the first three sprints. (Ready for refinement means Acceptance Criteria is complete.)

Each sprint has a number of regular meetings; for a 2 week long sprint:

1. **Stand-up**: Daily, 15 mins
2. **Backlog Refinement**: Weekly, 1-2 hours
3. **Estimating (Planning Poker)**: Weekly, 1-1.5 hours. Can be merged with the refinement meeting.
4. **Sprint Planning**: Once per sprint, 2 hours. Planning for the next sprint and beyond (not the current one).
5. **Sprint Review**: End of the sprint, 1-2 hours.
6. **Sprint Retrospective**: Once per sprint, 1 hour. Conducted after the Sprint Review.

At first glance, this may seem like a lot of meetings, however it’s important to note that these replace ad-hoc, haphazard meetings with regularly scheduled meetings. Plus, as the team get more efficient and/or the backlog is nearer completion, you may find you need less refinement and estimating. But all meetings are important to the ongoing improvement and velocity of the sprint they remain fairly critical to being able to deliver the product.

### Predictability [#](#predictability)

One of the tenets of Scrum is the inviolabilty of the Sprint: once a Sprint has begun, it isn’t changed. One of the jobs of the Scrum Master is to protect the sprint from outside interference, changes, and challenges.

The sprint planning, refinement, and estimation provides a mechanism to estimate effort, learn how much effort the team can expend in a sprint, and as a result, try and predict velocity. We can take that projected velocity, mix it with availability and other known commitments and deliver to the client or Product Owner a more reasonable expectation of what can be anticipated in terms of deliverable software and/or release planning.

During sprint planning, the team commits to the sprint goals and work toward them; the Scrum Master deals with the obstacles that life, clients and the universe put in the way; and ideally, at the end of the sprint, the work committed to is completed and demonstrated.

In cases where circumstances alter what the team think they can reasonably deliver against the sprint goals, the Scrum Master communicates that to the Product Owner, the team regroup, and revise the commitment. As continuous improvement is a goal, learning from these moments of failure to deliver is important, so that risk of ‘missing the sprint’ is minimised in future sprints.

### Continuous Improvement [#](#continuous-improvement)

The process of Scrum helps facilitate continuous improvement, particularly through the sprint meetings.

Each sprint is constantly reviewed, and practices that aren’t working are altered and proposed for the next sprint. Each successive sprint should be able to identify areas for improvement in velocity, predictability, and the ability to deliver the goals.

Stand-ups and Retrospectives are instrumental in this, with the goal of removing impediments improving the process and delivery..

Accessed Fri, 27 Apr 2018 03:34:10 +0000 from `https://engineering.hmn.md/how-we-work/process/agile/`

[Made by Humans](https://hmn.md)