"""Fill the site with realistic demo content so every page has something to show.

    python manage.py seed_demo            # add demo content (skips if courses already exist)
    python manage.py seed_demo --reset    # wipe content tables first
    python manage.py seed_demo --with-admin   # also create admin / admin12345 (change it!)
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from hub.models import (AboutSection, BlogPost, CoreValue, Course, CourseTopic, Event, EventHighlight,
                        MediaItem, Project, SiteSettings, TeamMember)


class Command(BaseCommand):
    help = "Create demo content for the Agentic AI Hub site."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--with-admin", action="store_true")

    def handle(self, *args, **opts):
        if opts["reset"]:
            for m in (Course, Event, BlogPost, MediaItem, Project, CoreValue, TeamMember, AboutSection):
                m.objects.all().delete()
        if Course.objects.exists():
            self.stdout.write("Content already exists. Use --reset to start over.")
            return

        s = SiteSettings.load()
        s.hero_headline = "Build AI agents that do real work."
        s.hero_subheadline = ("Hands-on courses, community events and open projects for people who build, "
                              "deploy and govern agentic AI.")
        s.tagline = "Learn to build AI that gets things done."
        s.story_title = "Where agents go from demo to daily work"
        s.story = ("Agentic AI Hub started as a Saturday meetup of engineers, analysts and founders trying to make "
                   "AI agents useful inside real organisations, not just in demos.\n\n"
                   "Today we run practical courses, host open community events and build projects with partners. "
                   "Everything we teach has been shipped by someone in our community first.")
        s.mission = ("To equip people and organisations with the practical skills to design, build and safely "
                     "deploy AI agents.")
        s.vision = "A community where anyone can turn an idea into a trustworthy AI agent that solves a local problem."
        s.contact_email = "hello@example.org"
        s.location = "Nairobi, Kenya"
        s.linkedin_url = "https://www.linkedin.com/"
        s.youtube_url = "https://www.youtube.com/"
        s.github_url = "https://github.com/"
        s.save()

        courses = [
            ("Foundations of Agentic AI", 3, "Understand how AI agents perceive, plan and act, and build your first working agent.",
             "Comfortable using a computer\nCuriosity about AI", 21, [
                 ("What makes an agent", "Agents versus chatbots and automations, with real examples."),
                 ("Prompting and tool use", "Give a model tools and write instructions it follows reliably."),
                 ("Your first agent", "Build and run a small agent that completes a multi-step task.")]),
            ("Building Agents with Python", 10, "Design, code and test production-style agents using Python and modern LLM APIs.",
             "Basic Python (functions, packages)\nA laptop with Python 3.10+", 45, [
                 ("Agent architectures", "Loops, planners, routers and when to use each."),
                 ("Memory and retrieval", "Give agents short and long-term memory with vector search."),
                 ("Evaluation and testing", "Measure whether an agent is actually getting better."),
                 ("Capstone project", "Ship an agent that solves a problem from your own work.")]),
            ("AI Agents for Business Leaders", 2, "Spot high-value agent use cases, estimate returns and manage the risks.",
             "", None, [
                 ("Finding the right use cases", "A simple scoring method for choosing where agents pay off."),
                 ("Risk, privacy and governance", "Policies, human oversight and audit trails that work in practice.")]),
            ("Multi-Agent Systems and Orchestration", 15, "Coordinate teams of specialised agents and keep them reliable at scale.",
             "Completed Building Agents with Python or equivalent experience", 90, [
                 ("Coordination patterns", "Supervisors, hand-offs and shared state."),
                 ("Observability", "Tracing, cost control and debugging failed runs."),
                 ("Deployment", "Run agents safely on cloud infrastructure.")]),
        ]
        today = timezone.localdate()
        for i, (title, days, summary, prereq, in_days, topics) in enumerate(courses):
            c = Course.objects.create(title=title, duration_days=days, summary=summary, prerequisites=prereq, order=i,
                                      next_cohort_date=(today + timedelta(days=in_days)) if in_days else None)
            for j, (t, d) in enumerate(topics):
                CourseTopic.objects.create(course=c, title=t, description=d, order=j)

        now = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0)
        events = [
            ("Agent Builders Meetup", 12, "Nairobi, Online option", "meetup, community, networking",
             "An open evening for anyone building with AI agents. Share what you're working on and get feedback.",
             ["Five-minute lightning demos", "Open mic for questions", "Meet local founders and engineers"]),
            ("Hands-on Workshop: Your First Tool-Using Agent", 30, "Nairobi", "workshop, beginners, Python",
             "A full-afternoon workshop where you leave with a working agent that uses real tools.",
             ["Bring your laptop, we provide API credits", "Pair programming with mentors", "Take-home starter repository"]),
            ("Responsible Agents: Safety and Governance Panel", 55, "Online", "panel, governance, safety",
             "Practitioners discuss how to keep agents accountable when they act on behalf of people.",
             ["Live Q&A with the panel", "Case studies from finance and health"]),
            ("Agentic AI Demo Day", 80, "Nairobi", "demo day, showcase",
             "Graduates of our cohorts present the agents they built to a room of potential partners and employers.",
             ["Ten live demos", "Awards for most useful agent", "Hiring and partnership corner"]),
            ("Intro to Agents (Recorded Session)", -25, "Online", "webinar, beginners",
             "A beginner-friendly walkthrough of what agents are and how to start.", ["Slides and recording shared with attendees"]),
        ]
        for title, offset, loc, tags, desc, hl in events:
            e = Event.objects.create(title=title, date=now + timedelta(days=offset), location=loc, tags=tags,
                                     description=desc)
            for j, h in enumerate(hl):
                EventHighlight.objects.create(event=e, text=h, order=j)

        posts = [
            ("What actually makes an AI system 'agentic'?", "Amina Njoroge",
             "A plain-language definition, and a quick test you can use on any product claiming to be an agent.",
             "People use the word agent for everything from chatbots to scheduled scripts.\n\n## A simple test\n\n"
             "An agent pursues a goal across several steps, chooses which tools to use, and checks its own progress.\n\n"
             "If a system only answers one question at a time, it's an assistant. If it plans, acts and adjusts, it's an agent.\n\n"
             "## Why it matters\n\nAgents can finish work, which also means they can make mistakes at scale. Design for oversight from day one."),
            ("Five lessons from our first agent cohort", "Daniel Otieno",
             "What worked, what broke, and what we changed after training 40 people to build agents.",
             "We ran our first cohort earlier this year.\n\n## Start with a boring problem\n\nThe best capstones solved dull, repeated tasks.\n\n"
             "## Evaluate early\n\nTeams that wrote tests for their agent in week one shipped better results."),
            ("A buyer's checklist for AI agent projects", "Wanjiru Kamau",
             "Ten questions to ask before commissioning an agent for your organisation.",
             "Before you spend a shilling, get clear answers to these questions.\n\n## Scope\n\nWhat is the single task this agent should own?\n\n"
             "## Oversight\n\nWho reviews its work, and how quickly can they intervene?"),
        ]
        for i, (t, a, d, c) in enumerate(posts):
            BlogPost.objects.create(title=t, author=a, description=d, content=c, date=today - timedelta(days=7 * (i + 1)))

        media = [
            ("Agents in 5 minutes", "A fast explainer on what agents are and where they help.", "landscape", "youtube",
             "https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
            ("Demo: a research agent in action", "Watch an agent plan, search and write a briefing.", "portrait", "tiktok",
             "https://www.tiktok.com/", True),
            ("Workshop highlights", "Moments from our hands-on workshop.", "landscape", "youtube",
             "https://www.youtube.com/watch?v=aqz-KE-bpKQ", True),
            ("Tip: test your agent first", "A 45-second tip on evaluating agents.", "portrait", "instagram",
             "https://www.instagram.com/", False),
        ]
        for i, (n, d, o, p, u, f) in enumerate(media):
            MediaItem.objects.create(name=n, description=d, orientation=o, platform=p, video_url=u, featured=f,
                                     date=today - timedelta(days=4 * i))

        Project.objects.create(title="Claims triage agent", client="Regional insurer", year=today.year,
                               description="An agent that reads incoming claims, checks policy rules and routes cases to the right team, cutting first-response time.",
                               tags="insurance, document AI, workflow", order=0)
        Project.objects.create(title="Farmer advisory assistant", client="Agri co-operative", year=today.year - 1,
                               description="A multilingual agent that answers crop questions by phone message and escalates tricky cases to extension officers.",
                               tags="agriculture, multilingual, SMS", order=1)
        Project.objects.create(title="Agent training programme", client="University partner", year=today.year,
                               description="A semester-long curriculum and lab environment teaching students to build and evaluate agents.",
                               tags="education, curriculum", order=2)

        for i, (t, d) in enumerate([
            ("Practical first", "We teach what we have shipped. Every lesson ends with something working."),
            ("Safety by design", "Agents act in the world, so oversight, privacy and accountability are built in."),
            ("Open community", "We share code, notes and recordings so others can learn and contribute."),
            ("Local relevance", "We build for the problems and languages of the communities we serve.")]):
            CoreValue.objects.create(title=t, description=d, order=i)

        for i, (n, r, b) in enumerate([
            ("Amina Njoroge", "Founder and Lead Instructor", "Machine learning engineer turned educator."),
            ("Daniel Otieno", "Head of Programmes", "Designs our curriculum and runs every cohort."),
            ("Wanjiru Kamau", "Community Lead", "Builds the meetups, partnerships and mentor network."),
            ("Brian Mwangi", "Engineering Mentor", "Ships production agents and reviews student projects.")]):
            TeamMember.objects.create(name=n, role=r, bio=b, order=i)

        AboutSection.objects.create(title="How we teach", order=0, body=(
            "Small cohorts, live building and mentor feedback. Each course ends with a project you can show.\n\n"
            "We keep our curriculum current as models and tools change."))
        AboutSection.objects.create(title="Partners and impact", order=1, body=(
            "We work with universities, enterprises and community groups. Contact us to run a private cohort for your team."))

        if opts["with_admin"]:
            U = get_user_model()
            if not U.objects.filter(username="admin").exists():
                U.objects.create_superuser("admin", "admin@example.org", "admin12345")
                self.stdout.write("Created demo admin user: admin / admin12345 (change this!)")
        self.stdout.write(self.style.SUCCESS("Demo content created."))
