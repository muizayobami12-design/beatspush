'use client';

export function ProducerDashboard() {
  return (
    <div className="bg-background text-on-background min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[60vh] min-h-[400px] w-full flex items-end pb-stack-lg px-margin-mobile md:px-margin-desktop border-b border-outline-variant/15">
        {/* Background */}
        <div className="absolute inset-0 z-0">
          <div
            className="bg-cover bg-center w-full h-full opacity-40 mix-blend-luminosity"
            style={{
              backgroundImage:
                'url(https://lh3.googleusercontent.com/aida-public/AB6AXuBImbN6zzzJYEd9PkKBVhLUyNHr9mh6bu0VgnfNdjiyu6PwQh-TSsE15pJ1JeiFhTDUItvV-Yo0AIdrNa33taAR_UFpuKqqsHZZHF-p3I4i2bnAS7Zuk0rYEplxSCORczOTSlwJJ8tIDaellgl6QFMxs0Eb4ZmufdwjXlH6ie1U4A74Xxpmrwnh7gfViMJ3jkQQonE0wVhuIo4GP5N6dqeUQT4iWzG-8G11AAxr5z8NM2z1Bt2j5mfR)',
            }}
          ></div>
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent"></div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 w-full max-w-container-max mx-auto flex flex-col md:flex-row gap-stack-md justify-between items-end">
          <div className="flex items-end gap-stack-md w-full">
            {/* Avatar */}
            <div className="w-32 h-32 md:w-48 md:h-48 rounded overflow-hidden border-2 border-surface-container-high shadow-2xl flex-shrink-0">
              <img
                className="w-full h-full object-cover"
                alt="Producer profile"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuB34cPUHF9_aRO7J2ElhiFPp8OknijDzCs0G5og-eoA0IaIo5ijBnaPMtcu9U9XmOmQM217VAReyH4OivPCfHdabu4n5g33bGp09uiyiIPZU1Vrt4JE-EQaZNA8t2IvDWDhZw4xdiM-jfChpIBKnMutoSTFDU0RXvnUzhviHsDyefKRVifcpI41WPqfMUeG0T3yVv4SejWialu8ehP18cWalY4SCJ_CYEk4ZMz0OUpVQEBPQrWKqRBD"
              />
            </div>

            <div className="mb-2">
              {/* Badges */}
              <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 bg-tertiary-container text-on-tertiary-container rounded font-label-sm text-label-sm border border-tertiary/20">
                  Afrobeats
                </span>
                <span className="px-3 py-1 bg-surface-container text-on-surface-variant rounded font-label-sm text-label-sm border border-outline-variant/30">
                  Lagos / London
                </span>
              </div>

              {/* Name & Title */}
              <h1 className="font-display-lg text-display-lg md:text-display-lg text-on-surface leading-tight mb-1">
                Oluwa Beats
              </h1>
              <p className="font-body-lg text-body-lg text-on-surface-variant">
                Multi-Platinum Producer & Sound Designer
              </p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col gap-3 w-full md:w-auto shrink-0 mt-stack-sm md:mt-0">
            <button className="w-full md:w-auto px-8 py-3 bg-secondary text-on-secondary font-label-sm text-label-sm font-bold rounded hover:bg-secondary-fixed transition-colors flex items-center justify-center gap-2">
              <span className="material-symbols-outlined">headset_mic</span>
              Request Custom Beat
            </button>
            <button className="w-full md:w-auto px-8 py-3 bg-transparent border border-tertiary text-tertiary font-label-sm text-label-sm font-bold rounded hover:bg-tertiary/10 transition-colors flex items-center justify-center gap-2">
              <span className="material-symbols-outlined">local_cafe</span>
              Tip Producer
            </button>
          </div>
        </div>
      </section>

      {/* Content Grid */}
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg flex flex-col gap-stack-lg">
        {/* Bento Grid: Stats & Bio */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-stack-sm md:gap-gutter">
          {/* Stats Card */}
          <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md flex flex-col justify-between col-span-1">
            <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-4">
              Network Value
            </h3>
            <div className="space-y-4">
              <div>
                <p className="font-headline-md text-headline-md text-secondary">14.2M+</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">Global Streams</p>
              </div>
              <div className="h-px w-full bg-outline-variant/20"></div>
              <div>
                <p className="font-headline-md text-headline-md text-secondary">3</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">Platinum Plaques</p>
              </div>
            </div>
          </div>

          {/* Bio Card */}
          <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md col-span-1 md:col-span-2">
            <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-4">
              Sonic Identity
            </h3>
            <p className="font-body-md text-body-md text-on-surface leading-relaxed text-opacity-90">
              Bridging traditional African polyrhythms with cutting-edge electronic synthesis. Oluwa Beats operates at the intersection of cultural heritage and modern global pop structures, delivering high-fidelity audio engineering and production for institutional artists and independent creators alike.
            </p>
            <div className="mt-stack-sm flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-surface-variant text-on-surface rounded font-label-sm text-label-sm">
                Logic Pro
              </span>
              <span className="px-3 py-1 bg-surface-variant text-on-surface rounded font-label-sm text-label-sm">
                Analog Synthesis
              </span>
              <span className="px-3 py-1 bg-surface-variant text-on-surface rounded font-label-sm text-label-sm">
                Vocal Production
              </span>
            </div>
          </div>
        </section>

        {/* Beat Store Section */}
        <section>
          <div className="flex justify-between items-end mb-stack-md border-b border-outline-variant/20 pb-4">
            <h2 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface">
              Beat Store
            </h2>
            <a href="#" className="font-label-sm text-label-sm text-secondary hover:underline">
              View All
            </a>
          </div>

          {/* Beat Table */}
          <div className="flex flex-col gap-0 border border-outline-variant/15 rounded-lg overflow-hidden">
            {/* Table Header */}
            <div className="grid grid-cols-12 gap-4 p-4 bg-surface-container border-b border-outline-variant/15 font-label-sm text-label-sm text-on-surface-variant uppercase">
              <div className="col-span-1 md:col-span-1">Play</div>
              <div className="col-span-7 md:col-span-5">Title</div>
              <div className="hidden md:block md:col-span-2">BPM / Key</div>
              <div className="hidden md:block md:col-span-2 text-right">Tags</div>
              <div className="col-span-4 md:col-span-2 text-right">License</div>
            </div>

            {/* Beat Row 1 */}
            <div className="grid grid-cols-12 gap-4 p-4 bg-surface-container-low border-b border-outline-variant/15 items-center hover:bg-surface-container transition-colors group">
              <div className="col-span-1 md:col-span-1">
                <button className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-primary group-hover:text-secondary group-hover:bg-secondary/10 transition-colors">
                  <span className="material-symbols-outlined text-[18px]">play_arrow</span>
                </button>
              </div>
              <div className="col-span-7 md:col-span-5 flex items-center gap-3">
                <div className="w-10 h-10 rounded bg-surface-container-highest overflow-hidden shrink-0">
                  <img
                    className="w-full h-full object-cover"
                    alt="Beat cover"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuAn1oO4-qe6ko0vgj9cbfUWXCXVPMTGlvk_beOvB43ho7SDNTIgbDADLpDMgYKZYpClXaOZyG7dEz8BRWIAvorHOWhCWibp9Qwn67BQ8mYnx27YfDAE6JneDyZUG2bbatCKekwwnUKPmBmSPG3yXvbBZoPNwAUkb3C1s5SenI373UAxHV8rVx6DX80Wexye5Cpfpp7zcGtNb67c23acaoPLZTHSGJiwggHulHLIjqTvZ-yZzk7eviIE"
                  />
                </div>
                <div>
                  <p className="font-body-md text-body-md font-semibold text-on-surface truncate">
                    Midnight in Ikoyi
                  </p>
                  <p className="font-label-sm text-label-sm text-on-surface-variant md:hidden">
                    105 BPM • Am
                  </p>
                </div>
              </div>
              <div className="hidden md:flex md:col-span-2 flex-col justify-center">
                <p className="font-label-sm text-label-sm text-on-surface">105</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">A Minor</p>
              </div>
              <div className="hidden md:flex md:col-span-2 justify-end items-center gap-1">
                <span className="px-2 py-0.5 bg-surface-variant text-on-surface-variant rounded font-label-sm text-[10px]">
                  Dark
                </span>
              </div>
              <div className="col-span-4 md:col-span-2 flex justify-end">
                <button className="px-4 py-2 bg-transparent border border-outline-variant rounded font-label-sm text-label-sm text-primary hover:border-secondary hover:text-secondary transition-colors">
                  ₦25,000
                </button>
              </div>
            </div>

            {/* Beat Row 2 */}
            <div className="grid grid-cols-12 gap-4 p-4 bg-surface-container-low border-b border-outline-variant/15 items-center hover:bg-surface-container transition-colors group">
              <div className="col-span-1 md:col-span-1">
                <button className="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center text-primary group-hover:text-secondary group-hover:bg-secondary/10 transition-colors">
                  <span className="material-symbols-outlined text-[18px]">play_arrow</span>
                </button>
              </div>
              <div className="col-span-7 md:col-span-5 flex items-center gap-3">
                <div className="w-10 h-10 rounded bg-surface-container-highest overflow-hidden shrink-0">
                  <img
                    className="w-full h-full object-cover"
                    alt="Beat cover"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuAn1oO4-qe6ko0vgj9cbfUWXCXVPMTGlvk_beOvB43ho7SDNTIgbDADLpDMgYKZYpClXaOZyG7dEz8BRWIAvorHOWhCWibp9Qwn67BQ8mYnx27YfDAE6JneDyZUG2bbatCKekwwnUKPmBmSPG3yXvbBZoPNwAUkb3C1s5SenI373UAxHV8rVx6DX80Wexye5Cpfpp7zcGtNb67c23acaoPLZTHSGJiwggHulHLIjqTvZ-yZzk7eviIE"
                  />
                </div>
                <div>
                  <p className="font-body-md text-body-md font-semibold text-on-surface truncate">
                    Afrosynth Wave
                  </p>
                  <p className="font-label-sm text-label-sm text-on-surface-variant md:hidden">
                    128 BPM • Em
                  </p>
                </div>
              </div>
              <div className="hidden md:flex md:col-span-2 flex-col justify-center">
                <p className="font-label-sm text-label-sm text-on-surface">128</p>
                <p className="font-label-sm text-label-sm text-on-surface-variant">E Minor</p>
              </div>
              <div className="hidden md:flex md:col-span-2 justify-end items-center gap-1">
                <span className="px-2 py-0.5 bg-surface-variant text-on-surface-variant rounded font-label-sm text-[10px]">
                  Upbeat
                </span>
              </div>
              <div className="col-span-4 md:col-span-2 flex justify-end">
                <button className="px-4 py-2 bg-transparent border border-outline-variant rounded font-label-sm text-label-sm text-primary hover:border-secondary hover:text-secondary transition-colors">
                  ₦18,000
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
