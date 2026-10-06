import { ArrowRight, Compass, Sparkles, Target } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

function OnboardingResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const profile = location.state?.profile;

  if (!profile) {
    return (
      <Page>
        <p className="text-sm text-slate-400">
          No assessment result available. Please complete the assessment first.
        </p>
      </Page>
    );
  }

  return (
    <Page>
      <div className="mx-auto max-w-3xl">
        <div className="nb-card rounded-2xl p-8">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10">
              <Sparkles className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <div className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-400">
                Assessment Complete
              </div>
              <h1 className="mt-1 text-2xl font-bold text-white">
                Your starting point
              </h1>
            </div>
          </div>

          <div className="mt-7 grid gap-4 sm:grid-cols-2">
            <Dimension label="Computer" level={profile.computer_knowledge} />
            <Dimension
              label="Networking"
              level={profile.networking_knowledge}
            />
            <Dimension
              label="Linux / CLI"
              level={profile.linux_cli_knowledge}
            />
            <Dimension
              label="Web Security"
              level={profile.web_security_knowledge}
            />
            <Dimension
              label="Practical Security"
              level={profile.practical_security_experience}
            />
            <Dimension
              label="Guidance Level"
              level={profile.challenge_recommendation}
            />
          </div>

          {profile.knowledge_gaps?.length > 0 && (
            <div className="mt-7">
              <SectionTitle icon={Target} title="Identified gaps" />
              <div className="mt-3 flex flex-wrap gap-2">
                {profile.knowledge_gaps.map((gap) => (
                  <span
                    key={gap}
                    className="rounded-lg border border-orange-500/20 bg-orange-500/5 px-3 py-1.5 text-xs text-orange-300"
                  >
                    {gap.replace(":", " · ")}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="mt-7">
            <SectionTitle icon={Compass} title="Recommended starting points" />
            <div className="mt-3 space-y-2">
              {profile.recommended_learning_paths?.map((slug) => (
                <div
                  key={slug}
                  className="rounded-xl border border-blue-500/20 bg-blue-500/5 px-4 py-3 text-sm text-blue-200"
                >
                  {slug.replace(/-/g, " ")}
                </div>
              ))}
            </div>
          </div>

          {profile.personalized_advice && (
            <p className="mt-7 rounded-xl border border-slate-800 bg-slate-950/40 p-4 text-sm leading-6 text-slate-300">
              {profile.personalized_advice}
            </p>
          )}

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navigate("/learning")}
              className="nb-button-primary inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold"
            >
              Start Learning
              <ArrowRight className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={() => navigate("/ctf")}
              className="nb-button-secondary inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold"
            >
              Explore CTF Challenges
            </button>

            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              className="nb-button-secondary inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    </Page>
  );
}

function Dimension({ label, level }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-600">
        {label}
      </div>
      <div className="mt-1 text-sm font-semibold text-white">
        {String(level || "NONE").replace(/_/g, " ")}
      </div>
    </div>
  );
}

function SectionTitle({ icon: Icon, title }) {
  return (
    <div className="flex items-center gap-2 text-sm font-bold text-white">
      <Icon className="h-4 w-4 text-blue-400" />
      {title}
    </div>
  );
}

function Page({ children }) {
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  );
}

export default OnboardingResultPage;
