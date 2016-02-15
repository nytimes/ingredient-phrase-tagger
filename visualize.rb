#!/usr/bin/env ruby

fn = ARGV.first
if fn.nil? || fn == ""
  puts "usage: visualize.rb FILENAME"
  exit(1)
end

def sentence(lines)
  prev_guess = nil
  prev_truth = nil
  guess_parts = []
  truth_parts = []

  lines.map do |line|
    cols = line.split("\t")
    token = cols.first
    guess = cols[-1]
    truth = cols[-2]

    # remove B/I prefix
    guess.sub!(/[BI]\-/, "")
    truth.sub!(/[BI]\-/, "")

    if prev_guess.nil? || prev_guess != guess
      guess_parts.push([guess])
      prev_guess = guess
    end

    if prev_truth.nil? || prev_truth != truth
      truth_parts.push([truth])
      prev_truth = truth
    end

    guess_parts.last.push(token)
    truth_parts.last.push(token)
  end

  g = "<div clas='guess'><strong>Guess: </strong>" + guess_parts.map do |p|
    type, *rest = *p
    str = rest.join(" ")
    %Q[<span class="#{type.downcase}">#{str}<span>#{type[0,2]}</span></span>]
  end.join("") + "</div>"

  t = "<div class='truth'><strong>Truth: </strong>" + truth_parts.map do |p|
    type, *rest = *p
    str = rest.join(" ")
    %Q[<span class="#{type.downcase}">#{str}<span>#{type[0,2]}</span></span>]
  end.join("") + "</div>"

  s = (guess_parts == truth_parts) ? "right" : "wrong"
  "<section class='#{s}'>#{t}#{g}</section>"
end

puts <<-EOT
<html>
<head>
<style>
body { font-family: sans-serif; font-size: 20px; line-height: 16px; text-align: center; }
section { padding: 80px 0; border-top: 2px solid #eee; opacity: 0.4; }
section.wrong { opacity: 1; }
div:not(:last-child) { margin-bottom: 25px; }
div.guess { }
div.truth { }
strong { font-weight: normal; text-transform: uppercase; font-size: 10px; color: #888; }
span { color: #333; padding: 0 5px; position: relative; }
span.name    { background: #fcc; }
span.qty     { background: #cfc; }
span.unit    { background: #ccf; }
span.comment { background: #ffc; }
span.other   { background: #eff; }
span span { padding: 2px; position: absolute; top: -14px; left: 0; line-height: 10px; font-size: 8px; color: #000; background-color: inherit; }
</style>
<body>
EOT

File.open(fn) do |f|
  s = []
  f.each_with_index do |line, i|
    if line.match(/^\s+$/)
      puts sentence(s)
      s = []
    else
      s.push(line.strip)
    end
  end
end

puts <<-EOT
</body>
</html>
EOT
