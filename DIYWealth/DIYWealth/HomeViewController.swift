//
//  ViewController.swift
//  DIYWealth
//
//  Created by John Walker on 10/01/2019.
//  Copyright © 2019 DIYWealth. All rights reserved.
//

import UIKit

/*extension StringProtocol where Index == String.Index {
    func index(of string: Self, options: String.CompareOptions = []) -> Index? {
        return range(of: string, options: options)?.lowerBound
    }
    func endIndex(of string: Self, options: String.CompareOptions = []) -> Index? {
        return range(of: string, options: options)?.upperBound
    }
    func indexes(of string: Self, options: String.CompareOptions = []) -> [Index] {
        var result: [Index] = []
        var start = startIndex
        while start < endIndex,
            let range = self[start..<endIndex].range(of: string, options: options) {
                result.append(range.lowerBound)
                start = range.lowerBound < range.upperBound ? range.upperBound :
                    index(range.lowerBound, offsetBy: 1, limitedBy: endIndex) ?? endIndex
        }
        return result
    }
    func ranges(of string: Self, options: String.CompareOptions = []) -> [Range<Index>] {
        var result: [Range<Index>] = []
        var start = startIndex
        while start < endIndex,
            let range = self[start..<endIndex].range(of: string, options: options) {
                result.append(range)
                start = range.lowerBound < range.upperBound ? range.upperBound :
                    index(range.lowerBound, offsetBy: 1, limitedBy: endIndex) ?? endIndex
        }
        return result
    }
}*/

/*extension Collection where Element: Equatable {
    func indexDistance(of element: Element) -> Int? {
        guard let index = index(of: element) else { return nil }
        return distance(from: startIndex, to: index)
    }
}*/

extension StringProtocol where Index == String.Index {
    func encodedOffset(of element: Element) -> Int? {
        return index(of: element)?.encodedOffset
    }
    func encodedOffset(of string: Self) -> Int? {
        return range(of: string)?.lowerBound.encodedOffset
    }
}

class HomeViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        
        let textView = UITextView(frame: view.bounds.insetBy(dx:10,dy:10))
        //let textView = UITextView(frame: CGRect.insetBy(dx: 10.0, dy: 10.0))
        
        //textView.isEditable = false
        
        //textView.textContainerInset = UIEdgeInsets.zero
        //textView.textContainer.lineFragmentPadding = 0
        //textView.layoutManager.usesFontLeading = false
        
        //let textView = UITextView()
        
        //textView.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(textView)
        
        let guide = view.safeAreaLayoutGuide
        NSLayoutConstraint.activate([
            textView.topAnchor.constraint(equalToSystemSpacingBelow: guide.topAnchor, multiplier: 1.0),
            guide.bottomAnchor.constraint(equalToSystemSpacingBelow: textView.bottomAnchor, multiplier: 1.0)
        ])
        
        let headFont = UIFont.boldSystemFont(ofSize: 25)
        let subheadFont = UIFont.boldSystemFont(ofSize: 20)
        let bodyFont = UIFont.systemFont(ofSize: 14)
        
        let text = try! String(contentsOfFile: Bundle.main.path(forResource: "HomeText", ofType: "txt")!)
        let attributedText = NSMutableAttributedString(string: text)
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(headFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(headFont.lineHeight)
            paragraphStyle.paragraphSpacing = ceil(headFont.pointSize / 2)
            
            let attributes = [
                NSAttributedString.Key.font: headFont,
                NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "About DIYWealth")!)
            let textLength = Int(text.encodedOffset(of: "Please read this")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.lineSpacing = 2
            paragraphStyle.paragraphSpacing = ceil(bodyFont.lineHeight / 2)
            
            paragraphStyle.alignment = .justified
            
            let attributes = [
                NSAttributedString.Key.font: bodyFont,
                //NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "Please read this")!)
            let textLength = Int(text.encodedOffset(of: "So you’ve decided")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.paragraphSpacing = ceil(subheadFont.lineHeight / 2)
            
            let attributes = [
                NSAttributedString.Key.font: subheadFont,
                NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "So you’ve decided")!)
            let textLength = Int(text.encodedOffset(of: "Good for you")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.lineSpacing = 2
            paragraphStyle.paragraphSpacing = ceil(bodyFont.lineHeight / 2)
            
            paragraphStyle.alignment = .justified
            
            let attributes = [
                NSAttributedString.Key.font: bodyFont,
                //NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "Good for you")!)
            let textLength = Int(text.encodedOffset(of: "How can DIYWealth")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.paragraphSpacing = ceil(subheadFont.lineHeight / 2)
            
            let attributes = [
                NSAttributedString.Key.font: subheadFont,
                NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "How can DIYWealth")!)
            let textLength = Int(text.encodedOffset(of: "We’re guessing that")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.lineSpacing = 2
            paragraphStyle.paragraphSpacing = ceil(bodyFont.lineHeight / 2)
            
            paragraphStyle.alignment = .justified
            
            let attributes = [
                NSAttributedString.Key.font: bodyFont,
                //NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "We’re guessing that")!)
            let textLength = Int(text.encodedOffset(of: "What are the benefits")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.paragraphSpacing = ceil(subheadFont.lineHeight / 2)
            
            let attributes = [
                NSAttributedString.Key.font: subheadFont,
                NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "What are the benefits")!)
            let textLength = Int(text.encodedOffset(of: "Simplistically,")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.lineSpacing = 2
            paragraphStyle.paragraphSpacing = ceil(bodyFont.lineHeight / 2)
            
            paragraphStyle.alignment = .justified
            
            let attributes = [
                NSAttributedString.Key.font: bodyFont,
                //NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "Simplistically,")!)
            let textLength = Int(text.encodedOffset(of: "How does DIYWealth")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.paragraphSpacing = ceil(subheadFont.lineHeight / 2)
            
            let attributes = [
                NSAttributedString.Key.font: subheadFont,
                NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "How does DIYWealth")!)
            let textLength = Int(text.encodedOffset(of: "DIYWealth follows")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.lineSpacing = 2
            paragraphStyle.paragraphSpacing = ceil(bodyFont.lineHeight / 2)
            
            paragraphStyle.alignment = .justified
            
            let attributes = [
                NSAttributedString.Key.font: bodyFont,
                //NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "DIYWealth follows")!)
            let textLength = Int(text.encodedOffset(of: "Who shouldn’t use")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(subheadFont.lineHeight)
            paragraphStyle.paragraphSpacing = ceil(subheadFont.lineHeight / 2)
            
            let attributes = [
                NSAttributedString.Key.font: subheadFont,
                NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "Who shouldn’t use")!)
            let textLength = Int(text.encodedOffset(of: "Do not invest in")!) - textLocation - 1
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        do {
            let paragraphStyle = NSMutableParagraphStyle()
            
            paragraphStyle.minimumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.maximumLineHeight = ceil(bodyFont.lineHeight)
            paragraphStyle.lineSpacing = 2
            paragraphStyle.paragraphSpacing = ceil(bodyFont.lineHeight / 2)
            
            paragraphStyle.alignment = .justified
            
            let attributes = [
                NSAttributedString.Key.font: bodyFont,
                //NSAttributedString.Key.foregroundColor: UIColor.purple,
                NSAttributedString.Key.paragraphStyle: paragraphStyle,
                ]
            
            let textLocation = Int(text.encodedOffset(of: "Do not invest in")!)
            let textLength = Int(text.encodedOffset(of: "more suitable.")!) - textLocation + 13
            
            attributedText.addAttributes(attributes, range: NSRange(location: textLocation, length: textLength))
        }
        
        
        
        textView.attributedText = attributedText
        
        
    }

}

